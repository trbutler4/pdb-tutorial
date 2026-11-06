{
  description = "Python 3.4 development environment for the pdb tutorial";

  # This release still packages the Python version used by the tutorial.
  inputs.nixpkgs = {
    url = "github:NixOS/nixpkgs/18.03";
    flake = false;
  };
  inputs.editorPkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs = { self, nixpkgs, editorPkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      tools = import editorPkgs { inherit system; };
    in {
      devShells.${system}.default = tools.mkShellNoCC {
        name = "pdb-tutorial-python34";
        # The language server uses its own modern Python, not the tutorial runtime.
        packages = [ pkgs.python34 tools.python3Packages.jedi-language-server ];
        shellHook = ''
          export PYTHONNOUSERSITE=1
        '';
      };
    };
}
