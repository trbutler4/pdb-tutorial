{
  description = "Python 3.4 development environment for the pdb tutorial";

  # This release still packages the Python version used by the tutorial.
  inputs.nixpkgs = {
    url = "github:NixOS/nixpkgs/18.03";
    flake = false;
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
    in {
      devShells.${system}.default = pkgs.stdenv.mkDerivation {
        name = "pdb-tutorial-python34";
        buildInputs = [ pkgs.python34 ];
        shellHook = ''
          export PYTHONNOUSERSITE=1
        '';
      };
    };
}
