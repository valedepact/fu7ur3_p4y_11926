create table customers (
    id bigint generated always as identity primary key,
    name text not null,
    phone text
    add column credit_limit numeric;
);

create table item_classes (
    id bigint generated always as identity primary key,
    name text not null unique,
    base_price numeric not null
    add column unit_cost numeric not null default 0,
    add column wash_minutes integer not null default 30;
);

create table loads (
    id bigint generated always as identity primary key,
    dropped_off_at timestamptz not null,
    customer_id bigint not null references customers(id),
    item_class_id bigint not null references item_classes(id),
    quantity integer not null,
    price_charged numeric not null,
    status text not null default 'dropped_off',
    expected_pickup_date date,
    payment_status text not null default 'owing'
    add column unit_cost numeric not null default 0,
    add column amount_paid numeric not null default 0;
);

create table expenses (
    id bigint generated always as identity primary key,
    date date not null,
    category text not null,
    amount numeric not null,
    note text
);

create table business_settings (
    id integer primary key,
    daily_operating_minutes integer not null default 600,
    abandonment_days integer not null default 14
);