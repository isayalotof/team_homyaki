import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/tours_provider.dart';
import '../widgets/tour_card.dart';

class ToursScreen extends StatefulWidget {
  @override
  _ToursScreenState createState() => _ToursScreenState();
}

class _ToursScreenState extends State<ToursScreen> {
  bool _isInit = true;
  final _searchController = TextEditingController();
  double _minPrice = 0;
  double _maxPrice = 500000;
  String _sortBy = 'price_asc';

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_isInit) {
      Provider.of<ToursProvider>(context).fetchTours();
      _isInit = false;
    }
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _applyFilters() {
    Provider.of<ToursProvider>(context, listen: false).fetchTours(
      search: _searchController.text,
      minPrice: _minPrice,
      maxPrice: _maxPrice,
      sortBy: _sortBy,
    );
  }

  @override
  Widget build(BuildContext context) {
    final toursData = Provider.of<ToursProvider>(context);
    final tours = toursData.tours;
    final isLoading = toursData.isLoading;

    return Scaffold(
      appBar: AppBar(
        title: Text('Туры'),
        backgroundColor: Theme.of(context).primaryColor,
      ),
      body: Column(
        children: [
          _buildSearchBar(),
          _buildFilterBar(),
          Expanded(
            child: isLoading
                ? Center(child: CircularProgressIndicator())
                : tours.isEmpty
                    ? Center(child: Text('Нет доступных туров'))
                    : ListView.builder(
                        padding: EdgeInsets.symmetric(vertical: 8),
                        itemCount: tours.length,
                        itemBuilder: (ctx, i) => TourCard(
                          tour: tours[i],
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

  Widget _buildSearchBar() {
    return Padding(
      padding: EdgeInsets.all(16),
      child: TextField(
        controller: _searchController,
        decoration: InputDecoration(
          hintText: 'Поиск туров',
          prefixIcon: Icon(Icons.search),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide.none,
          ),
          filled: true,
          fillColor: Colors.grey[200],
          contentPadding: EdgeInsets.symmetric(vertical: 0),
          suffixIcon: IconButton(
            icon: Icon(Icons.clear),
            onPressed: () {
              _searchController.clear();
              _applyFilters();
            },
          ),
        ),
        onSubmitted: (_) => _applyFilters(),
      ),
    );
  }

  Widget _buildFilterBar() {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      color: Colors.grey[100],
      child: Row(
        children: [
          Expanded(
            child: TextButton.icon(
              onPressed: () {
                _showPriceFilterDialog();
              },
              icon: Icon(Icons.monetization_on),
              label: Text('Цена'),
            ),
          ),
          Expanded(
            child: TextButton.icon(
              onPressed: () {
                _showSortDialog();
              },
              icon: Icon(Icons.sort),
              label: Text('Сортировка'),
            ),
          ),
          Expanded(
            child: TextButton.icon(
              onPressed: () {
                _showFilterDialog();
              },
              icon: Icon(Icons.filter_list),
              label: Text('Фильтры'),
            ),
          ),
        ],
      ),
    );
  }

  void _showPriceFilterDialog() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text('Диапазон цен'),
        content: Container(
          height: 100,
          child: Column(
            children: [
              RangeSlider(
                values: RangeValues(_minPrice, _maxPrice),
                min: 0,
                max: 500000,
                divisions: 50,
                labels: RangeLabels(
                  '${_minPrice.round()} ₽',
                  '${_maxPrice.round()} ₽',
                ),
                onChanged: (RangeValues values) {
                  setState(() {
                    _minPrice = values.start;
                    _maxPrice = values.end;
                  });
                },
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('${_minPrice.round()} ₽'),
                  Text('${_maxPrice.round()} ₽'),
                ],
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(ctx).pop();
            },
            child: Text('Отмена'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(ctx).pop();
              _applyFilters();
            },
            child: Text('Применить'),
          ),
        ],
      ),
    );
  }

  void _showSortDialog() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text('Сортировка'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            RadioListTile<String>(
              title: Text('По цене (сначала дешевле)'),
              value: 'price_asc',
              groupValue: _sortBy,
              onChanged: (value) {
                setState(() {
                  _sortBy = value!;
                });
              },
            ),
            RadioListTile<String>(
              title: Text('По цене (сначала дороже)'),
              value: 'price_desc',
              groupValue: _sortBy,
              onChanged: (value) {
                setState(() {
                  _sortBy = value!;
                });
              },
            ),
            RadioListTile<String>(
              title: Text('По дате (сначала новые)'),
              value: 'date_desc',
              groupValue: _sortBy,
              onChanged: (value) {
                setState(() {
                  _sortBy = value!;
                });
              },
            ),
            RadioListTile<String>(
              title: Text('По популярности'),
              value: 'popularity',
              groupValue: _sortBy,
              onChanged: (value) {
                setState(() {
                  _sortBy = value!;
                });
              },
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(ctx).pop();
            },
            child: Text('Отмена'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(ctx).pop();
              _applyFilters();
            },
            child: Text('Применить'),
          ),
        ],
      ),
    );
  }

  void _showFilterDialog() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text('Дополнительные фильтры'),
        content: Text('Здесь будут дополнительные фильтры'),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(ctx).pop();
            },
            child: Text('Закрыть'),
          ),
        ],
      ),
    );
  }
} 