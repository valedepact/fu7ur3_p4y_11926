class PickupRequest {
  final int id;
  final String customerName;
  final String phone;
  final String address;
  final String requestedAt;
  final String status;
  final String? scheduledDate;
  final String? notes;
  final int? collectedLoadId;

  PickupRequest({
    required this.id, required this.customerName, required this.phone, required this.address,
    required this.requestedAt, required this.status, this.scheduledDate, this.notes, this.collectedLoadId,
  });

  factory PickupRequest.fromJson(Map<String, dynamic> json) {
    return PickupRequest(
      id: json['id'], customerName: json['customer_name'], phone: json['phone'], address: json['address'],
      requestedAt: json['requested_at'], status: json['status'], scheduledDate: json['scheduled_date'],
      notes: json['notes'], collectedLoadId: json['collected_load_id'],
    );
  }
}