-density_ksp_type  gmres -density_pc_type  asm
-velocity_ksp_type gmres -velocity_pc_type asm
-phi_ksp_type      cg -phi_pc_type hypre -phi_pc_hypre_type boomeramg -phi_ksp_knoll
-pressure_ksp_type cg -pressure_pc_type asm
