create table customers (
    id bigint generated always as identity primary key,
    name text not null,
    phone text
);

create table item_classes (
    id bigint generated always as identity primary key,
    name text not null unique,
    base_price numeric not null
);

create table loads (
    id bigint generated always as identity primary key,
    date date not null,
    customer_id bigint not null references customers(id),
    item_class_id bigint not null references item_classes(id),
    quantity integer not null,
    price_charged numeric not null
);

create table expenses (
    id bigint generated always as identity primary key,
    date date not null,
    category text not null,
    amount numeric not null,
    note text
);