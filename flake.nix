{
  description = "Python 3.15 development environment for the pdb tutorial";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      python = pkgs.python315.overrideAttrs (old: {
        version = "3.15.2";
        # The security release changed the context of nixpkgs' MIME patch.
        patches = builtins.filter
          (patch: builtins.baseNameOf (toString patch) != "mimetypes.patch")
          old.patches ++ [ ./nix/python315-mimetypes.patch ];
        src = pkgs.fetchurl {
          url = "https://www.python.org/ftp/python/3.15.2/Python-3.15.2.tar.xz";
          sha256 = "8b5536d280142ecf6cdfe15d12a21ba1c65e300bbf7b28a8d0cdb849575797de";
        };
      });
    in {
      devShells.${system}.default = pkgs.mkShellNoCC {
        name = "pdb-tutorial-python315";
        packages = [ python ];
        shellHook = ''
          export PYTHONNOUSERSITE=1
        '';
      };
    };
}
