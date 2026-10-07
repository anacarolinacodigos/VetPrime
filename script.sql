CREATE DATABASE VetPrime;
USE vetprime;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha VARCHAR(100) NOT NULL
);

CREATE TABLE tutores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf_criptografado VARCHAR(255) NOT NULL,
    telefone VARCHAR(20) NOT NULL
);

CREATE TABLE pets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    especie VARCHAR(50) NOT NULL,
    raca VARCHAR(50),
    tutor_id INT NOT NULL,
    CONSTRAINT fk_pets_tutores FOREIGN KEY (tutor_id) REFERENCES tutores(id) 
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE agendamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data_agendamento VARCHAR(50) NOT NULL,
    mes VARCHAR(20) NOT NULL,
    observacao VARCHAR(255),
    tutor_id INT NOT NULL,
    pet_id INT NOT NULL,
    CONSTRAINT fk_agendamentos_tutores FOREIGN KEY (tutor_id) REFERENCES tutores(id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_agendamentos_pets FOREIGN KEY (pet_id) REFERENCES pets(id) 
        ON DELETE CASCADE ON UPDATE CASCADE
);

INSERT INTO usuarios (nome, email, senha) VALUES 
('Dr. Carlos Silva', 'carlos@vetprime.com', '123456'),
('Recepção VetPrime', 'recepcao@vetprime.com', '123456');

INSERT INTO usuarios (nome, email, senha) 
VALUES ('Dra. Ana Carolina', 'anacarolvetprime@com', '838487');

INSERT INTO tutores (nome, cpf_criptografado, telefone) VALUES 
('João da Silva', '71296066142=', '(11) 98888-1111'),
('Maria Oliveira', '8560058778=', '(11) 97777-2222'),
('Pedro Santos', '96065400857=', '(11) 96666-3333');

INSERT INTO pets (nome, especie, raca, tutor_id) VALUES 
('Thor', 'Cão', 'Golden Retriever', 1),
('Mel', 'Gato', 'Siamês', 2),
('Bob', 'Cão', 'Poodle', 3);

INSERT INTO agendamentos (data_agendamento, mes, observacao, tutor_id, pet_id) VALUES 
('2026-10-15 14:00', 'Outubro', 'Vacina V10', 1, 1),
('2026-11-03 09:30', 'Novembro', 'Consulta Geral de Rotina', 2, 2),
('2026-12-10 16:00', 'Dezembro', 'Banho e Tosa', 3, 3);

SELECT id, nome, email FROM usuarios WHERE email = 'carlos@vetprime.com' AND senha = '123456';
SELECT * FROM tutores WHERE nome LIKE '%João%';

SELECT 
    pets.id AS pet_id,
    pets.nome AS nome_pet,
    pets.especie,
    pets.raca,
    tutores.nome AS nome_tutor
FROM pets
LEFT JOIN tutores ON pets.tutor_id = tutores.id;

SELECT 
    agendamentos.id AS agendamento_id,
    agendamentos.mes,
    agendamentos.data_agendamento,
    tutores.nome AS nome_tutor,
    tutores.cpf_criptografado,
    pets.nome AS nome_pet,
    pets.especie AS especie_pet,
    agendamentos.observacao
FROM agendamentos
JOIN tutores ON agendamentos.tutor_id = tutores.id
JOIN pets ON agendamentos.pet_id = pets.id
ORDER BY agendamentos.mes ASC, agendamentos.data_agendamento ASC;

UPDATE tutores SET telefone = '(11) 99999-0000' WHERE id = 1;
