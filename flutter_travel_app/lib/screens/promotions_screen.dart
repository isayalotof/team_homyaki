import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/tours_provider.dart';
import '../widgets/tour_card.dart';

class PromotionsScreen extends StatefulWidget {
  @override
  _PromotionsScreenState createState() => _PromotionsScreenState();
}

class _PromotionsScreenState extends State<PromotionsScreen> {
  bool _isInit = true;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_isInit) {
      Provider.of<ToursProvider>(context).fetchPromotedTours();
      _isInit = false;
    }
  }

  @override
  Widget build(BuildContext context) {
    final toursData = Provider.of<ToursProvider>(context);
    final promotedTours = toursData.promotedTours;
    final isLoading = toursData.isLoading;

    return Scaffold(
      appBar: AppBar(
        title: Text('Акции и спецпредложения'),
        backgroundColor: Theme.of(context).primaryColor,
      ),
      body: Column(
        children: [
          Container(
            padding: EdgeInsets.all(16),
            color: Theme.of(context).primaryColor.withOpacity(0.1),
            child: Text(
              'Специальные предложения и скидки на лучшие туры по России',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.center,
            ),
          ),
          Expanded(
            child: isLoading
                ? Center(child: CircularProgressIndicator())
                : promotedTours.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              Icons.local_offer_off,
                              size: 64,
                              color: Colors.grey,
                            ),
                            SizedBox(height: 16),
                            Text(
                              'Нет активных акций',
                              style: TextStyle(
                                fontSize: 18,
                                color: Colors.grey,
                              ),
                            ),
                          ],
                        ),
                      )
                    : ListView.builder(
                        padding: EdgeInsets.symmetric(vertical: 8),
                        itemCount: promotedTours.length,
                        itemBuilder: (ctx, i) => TourCard(
                          tour: promotedTours[i],
                          onTap: () {
                            // Navigate to tour details
                          },
                        ),
                      ),
          ),
        ],
      ),
    );
  }
} 