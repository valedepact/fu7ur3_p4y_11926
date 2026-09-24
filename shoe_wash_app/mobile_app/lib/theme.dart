import 'package:flutter/material.dart';

class AppColors {
  static const primary = Color(0xFF2563EB);
  static const success = Color(0xFF16A34A);
  static const successBg = Color(0xFFDCFCE7);
  static const danger = Color(0xFFEF4444);
  static const dangerBg = Color(0xFFFEE2E2);
  static const warning = Color(0xFFD97706);
  static const warningBg = Color(0xFFFEF3C7);
  static const bg = Color(0xFFF3F6FB);
  static const ink = Color(0xFF14213D);
  static const inkSoft = Color(0xFF64748B);
}

Color statusColor(String status) {
  switch (status) {
    case 'washing': return AppColors.warning;
    case 'ready': return AppColors.primary;
    case 'picked_up':
    case 'delivered': return AppColors.success;
    case 'abandoned': return AppColors.danger;
    default: return AppColors.inkSoft;
  }
}

Color statusBg(String status) {
  switch (status) {
    case 'washing': return AppColors.warningBg;
    case 'ready': return const Color(0xFFDBEAFE);
    case 'picked_up':
    case 'delivered': return AppColors.successBg;
    case 'abandoned': return AppColors.dangerBg;
    default: return const Color(0xFFE2E8F0);
  }
}

Color paymentColor(String status) {
  switch (status) {
    case 'paid': return AppColors.success;
    case 'partial': return AppColors.warning;
    default: return AppColors.danger;
  }
}

Color paymentBg(String status) {
  switch (status) {
    case 'paid': return AppColors.successBg;
    case 'partial': return AppColors.warningBg;
    default: return AppColors.dangerBg;
  }
}