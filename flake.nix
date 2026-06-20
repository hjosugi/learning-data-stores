{
  description = "Development shell for data-store learning labs";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { nixpkgs, ... }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "aarch64-darwin"
        "x86_64-darwin"
      ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in {
      devShells = forAllSystems (system:
        let
          pkgs = import nixpkgs { inherit system; };
          python = pkgs.python3.withPackages (ps: [
            ps.duckdb
          ]);
        in {
          default = pkgs.mkShell {
            packages = [
              python
              pkgs.duckdb
              pkgs.uv
            ];

            shellHook = ''
              echo "learning-data-stores dev shell"
              echo "Try: python3 projects/sqlite-workload-lab/test_app.py"
              echo "Try: python3 projects/duckdb-analytics-lab/app.py"
              echo "Try: python3 projects/vector-search-lab/test_app.py"
            '';
          };
        });
    };
}
