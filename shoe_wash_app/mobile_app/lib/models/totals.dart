class Totals {
  final double sales;
  final double expenses;
  final double balance;

  Totals({required this.sales, required this.expenses, required this.balance});

  factory Totals.fromJson(Map<String, dynamic> json) {
    return Totals(
      sales: (json['sales'] as num).toDouble(),
      expenses: (json['expenses'] as num).toDouble(),
      balance: (json['balance'] as num).toDouble(),
    );
  }
}