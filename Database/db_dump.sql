create table "Languages"
(
    lang_id  serial       not null
        constraint languages_pk
            primary key,
    name     varchar(150) not null,
    lang_key varchar      not null
);

create table "Clients"
(
    id      integer not null
        constraint clients_pk
            primary key,
    name    varchar,
    surname varchar,
    lang_id integer default 1
        constraint clients_languages_lang_id_fk
            references "Languages"
            on update cascade on delete cascade
);

create unique index languages_lang_key_uindex
    on "Languages" (lang_key);

create table "Cities"
(
    c_id       integer not null
        constraint cities_pk
            primary key,
    city_name  varchar not null,
    country_id varchar
);

create table city_client
(
    client_id integer
        constraint city_client_clients_id_fk
            references "Clients"
            on update cascade on delete cascade,
    city_id   integer
        constraint city_client_cities_c_id_fk
            references "Cities"
            on update cascade on delete cascade
);
