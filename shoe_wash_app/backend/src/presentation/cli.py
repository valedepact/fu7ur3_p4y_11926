from datetime import date, timedelta

from domain import Customer, ExpenseCategory, LoadStatus


class Cli:
    def __init__(self, record_load, record_expense, get_period_totals,
                 update_load_status, mark_load_paid, customer_repo, item_class_repo):
        self._record_load = record_load
        self._record_expense = record_expense
        self._get_period_totals = get_period_totals
        self._update_load_status = update_load_status
        self._mark_load_paid = mark_load_paid
        self._customer_repo = customer_repo
        self._item_class_repo = item_class_repo

    def run(self):
        while True:
            print("\n1. Log a load  2. Log an expense  3. View totals  "
                  "4. Update load status  5. Mark load paid  6. Exit")
            choice = input("Choose: ").strip()

            if choice == "1":
                self._log_load()
            elif choice == "2":
                self._log_expense()
            elif choice == "3":
                self._view_totals()
            elif choice == "4":
                self._update_status()
            elif choice == "5":
                self._mark_paid()
            elif choice == "6":
                break
            else:
                print("Not a valid option.")

    def _log_load(self):
        name = input("Customer name: ").strip()
        customer = self._customer_repo.add(Customer(id=None, name=name))

        for item_class in self._item_class_repo.list_all():
            print(f"{item_class.id}: {item_class.name} (default {item_class.base_price})")
        item_class_id = int(input("Item class id: "))
        quantity = int(input("Quantity: "))
        price_input = input("Price charged (blank for default): ").strip()
        price = float(price_input) if price_input else None
        pickup_input = input("Expected pickup date YYYY-MM-DD (blank if unknown): ").strip()
        pickup = date.fromisoformat(pickup_input) if pickup_input else None

        result = self._record_load.execute(
            customer_id=customer.id,
            item_class_id=item_class_id,
            quantity=quantity,
            price_charged=price,
            expected_pickup_date=pickup,
        )
        load = result.load
        print(f"Logged load #{load.id}: {quantity} item(s), {load.total} total, status={load.status}")
        for warning in result.warnings:
            print(f"WARNING: {warning}")
            
    def _log_expense(self):
        print(
            f"Categories: {ExpenseCategory.SUPPLIES}, {ExpenseCategory.UTILITIES}, "
            f"{ExpenseCategory.MACHINE_UPKEEP}, {ExpenseCategory.OTHER}"
        )
        category = input("Category: ").strip()
        amount = float(input("Amount: "))
        note = input("Note (optional): ").strip() or None

        expense = self._record_expense.execute(category=category, amount=amount, note=note)
        print(f"Logged expense #{expense.id}: {expense.amount}")

    def _view_totals(self):
        print("1. Today  2. This week  3. This month  4. Custom")
        choice = input("Choose: ").strip()
        today = date.today()

        if choice == "1":
            start = end = today
        elif choice == "2":
            start, end = today - timedelta(days=today.weekday()), today
        elif choice == "3":
            start, end = today.replace(day=1), today
        elif choice == "4":
            start = date.fromisoformat(input("Start date (YYYY-MM-DD): ").strip())
            end = date.fromisoformat(input("End date (YYYY-MM-DD): ").strip())
        else:
            print("Not a valid option.")
            return

        totals = self._get_period_totals.execute(start, end)
        print(f"\nSales: {totals.sales}")
        print(f"Expenses: {totals.expenses}")
        print(f"Balance: {totals.balance}")

    def _update_status(self):
        load_id = int(input("Load id: "))
        print(f"Statuses: {LoadStatus.DROPPED_OFF}, {LoadStatus.WASHING}, "
              f"{LoadStatus.READY}, {LoadStatus.PICKED_UP}")
        new_status = input("New status: ").strip()
        load = self._update_load_status.execute(load_id, new_status)
        print(f"Load #{load.id} is now {load.status}")

    def _mark_paid(self):
        load_id = int(input("Load id: "))
        load = self._mark_load_paid.execute(load_id)
        print(f"Load #{load.id} marked {load.payment_status}")