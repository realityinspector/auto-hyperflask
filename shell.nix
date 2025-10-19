{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = (import ./replit.nix { inherit pkgs; }).deps;

  shellHook = ''
    # Source virtual environment if it exists
    if [ -d venv ]; then
      source venv/bin/activate
    fi

    # Set library path for compiled Python extensions and Playwright
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.xorg.libX11}/lib:${pkgs.systemd}/lib:${pkgs.glib.out}/lib:${pkgs.nss.out}/lib:${pkgs.nspr.out}/lib:${pkgs.atk.out}/lib:${pkgs.at-spi2-atk.out}/lib:${pkgs.cups.out}/lib:${pkgs.dbus.lib}/lib:${pkgs.xorg.libXcomposite.out}/lib:${pkgs.xorg.libXdamage.out}/lib:${pkgs.xorg.libXext.out}/lib:${pkgs.xorg.libXfixes.out}/lib:${pkgs.xorg.libXrandr.out}/lib:${pkgs.libxkbcommon.out}/lib:${pkgs.mesa.out}/lib:${pkgs.expat.out}/lib:${pkgs.alsa-lib.out}/lib:${pkgs.pango.out}/lib:${pkgs.cairo.out}/lib:$LD_LIBRARY_PATH"
  '';
}
