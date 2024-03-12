with (import <nixpkgs> {});
with python311Packages;
let
  tkinterPath = lib.getLib tkinter;
in
stdenv.mkDerivation {
  name = "python-tk";
  buildInputs = [
    # Python requirements.
    python311Full
    tkinter
  ];
  src = null;
  shellHook = ''
    set -e
    poetry install

    # Use tkinter from System, patch activate script
    ACTIVATE_SCRIPT_PATH="$(poetry env info --path)/bin/activate"
    export TKINTER_PATH="${tkinterPath}/lib/python3.11/site-packages"
    echo "tkinter at:   $TKINTER_PATH"
    echo ""

    PATCH="export PYTHONPATH=\""

    PATCH="$PATCH\$TKINTER_PATH"

    PATCH="$PATCH\""

    if grep -q "$PATCH" "$ACTIVATE_SCRIPT_PATH"; then
        echo "venv is already patched."
    else
        echo "patching $ACTIVATE_SCRIPT_PATH to use tkinter from nixos..."
        sed -i "\$i$PATCH" $ACTIVATE_SCRIPT_PATH
    fi

    poetry shell
  '';
}
