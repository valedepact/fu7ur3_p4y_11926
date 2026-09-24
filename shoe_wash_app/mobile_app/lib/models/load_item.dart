class LoadItem {
  final int? id;
  final int itemClassId;
  final int quantity;
  final double priceCharged;
  final double unitCost;

  LoadItem({this.id, required this.itemClassId, required this.quantity, required this.priceCharged, this.unitCost = 0});

  double get total => priceCharged * quantity;

  factory LoadItem.fromJson(Map<String, dynamic> json) {
    return LoadItem(
      id: json['id'],
      itemClassId: json['item_class_id'],
      quantity: json['quantity'],
      priceCharged: (json['price_charged'] as num).toDouble(),
      unitCost: (json['unit_cost'] as num?)?.toDouble() ?? 0,
    );
  }
}