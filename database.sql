CREATE TABLE IF NOT EXTISTS urls (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name varchar(255) NOT NULL,
    created_at date NOT NULL
);
