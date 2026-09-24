class ItemClass {
  final int id;
  final String name;
  final double basePrice;
  final double unitCost;
  final int washMinutes;

  ItemClass({
    required this.id,
    required this.name,
    required this.basePrice,
    this.unitCost = 0,
    this.washMinutes = 30,
  });

  factory ItemClass.fromJson(Map<String, dynamic> json) {
    return ItemClass(
      id: json['id'],
      name: json['name'],
      basePrice: (json['base_price'] as num).toDouble(),
      unitCost: (json['unit_cost'] as num?)?.toDouble() ?? 0,
      washMinutes: (json['wash_minutes'] as num?)?.toInt() ?? 30,
    );
  }
}