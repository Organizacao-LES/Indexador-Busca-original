INSERT INTO usuario (
    nome,
    login,
    email,
    senha_hash,
    perfil,
    ativo
)
VALUES (
    'Administrador',
    'admin',
    'admin@ifes.edu.br',
    '$2b$12$W5u0Luweo.Tw/T/rHJOshOKS470nstrvajRpV39e9msL.gkaibCma',
    'ADMIN',
    TRUE
)
ON CONFLICT (login) DO NOTHING;
