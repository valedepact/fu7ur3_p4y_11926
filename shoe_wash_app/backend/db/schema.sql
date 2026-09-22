create table customers (
    id bigint generated always as identity primary key,
    name text not null,
    phone text,
    credit_limit numeric
);

create table item_classes (
    id bigint generated always as identity primary key,
    name text not null unique,
    base_price numeric not null,
    unit_cost numeric not null default 0,
    wash_minutes integer not null default 30
);

create table loads (
    id bigint generated always as identity primary key,
    dropped_off_at timestamptz not null,
    customer_id bigint not null references customers(id),
    item_class_id bigint not null references item_classes(id),
    quantity integer not null,
    price_charged numeric not null,
    unit_cost numeric not null default 0,
    amount_paid numeric not null default 0,
    status text not null default 'dropped_off',
    expected_pickup_date date,
    payment_status text not null default 'owing',
    delivery_method text not null default 'walk_in',
    pickup_address text,
    delivery_address text
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

insert into business_settings (id, daily_operating_minutes, abandonment_days)
values (1, 600, 14);

create table pickup_requests (
    id bigint generated always as identity primary key,
    customer_name text not null,
    phone text not null,
    address text not null,
    requested_at timestamptz not null,
    status text not null default 'requested',
    scheduled_date date,
    notes text,
    collected_load_id bigint references loads(id)
);
