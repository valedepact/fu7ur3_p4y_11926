class Expense {
  final int id;
  final String date;
  final String category;
  final double amount;
  final String? note;

  Expense({
    required this.id,
    required this.date,
    required this.category,
    required this.amount,
    this.note,
  });

  factory Expense.fromJson(Map<String, dynamic> json) {
    return Expense(
      id: json['id'],
      date: json['date'],
      category: json['category'],
      amount: (json['amount'] as num).toDouble(),
      note: json['note'],
    );
  }
}