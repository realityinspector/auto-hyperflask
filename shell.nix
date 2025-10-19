{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = (import ./replit.nix { inherit pkgs; }).deps;

  shellHook = ''
    # Source virtual environment if it exists
    if [ -d venv ]; then
      source venv/bin/activate
    fi

    # Set library path for compiled Python extensions
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH"
  '';
}
