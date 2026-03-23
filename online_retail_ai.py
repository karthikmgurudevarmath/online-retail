import random
import time
import pandas as pd

# --- 1. Dynamic Pricing Strategies ---
def calculate_dynamic_price(base_price, demand_factor, competitor_price, inventory_level, max_inventory):
    """
    Adjust price based on demand, competitor, and inventory.
    demand_factor: 0.0 to 2.0 (1.0 is normal)
    """
    # Base adjustment on demand
    price = base_price * demand_factor
    
    # Adjust based on inventory (if inventory is high, lower price; if low, raise price)
    inventory_ratio = inventory_level / max_inventory
    if inventory_ratio > 0.8:
        price *= 0.9 # 10% discount to clear stock
    elif inventory_ratio < 0.2:
        price *= 1.15 # 15% markup due to scarcity
        
    # Match competitor price if ours is significantly higher, but maintain a minimum margin
    if price > competitor_price * 1.1:
        price = max(competitor_price * 0.95, base_price * 0.8) # undercut slightly but don't go below 80% of base
        
    return round(price, 2)

# --- 2. Personalized Recommendations ---
def get_personalized_recommendations(user_profile, products_df):
    """
    Recommend products based on user's preferred categories and past purchases.
    """
    preferred_categories = user_profile.get('preferred_categories', [])
    past_purchases = user_profile.get('past_purchases', [])
    
    # Filter products matching preferred categories
    recommendations = products_df[products_df['category'].isin(preferred_categories)].copy()
    
    # Exclude already purchased items
    if not recommendations.empty:
        recommendations = recommendations[~recommendations['product_id'].isin(past_purchases)]
        
        # Sort by a 'popularity' score (simulated here)
        recommendations['recommendation_score'] = recommendations['base_price'] * [random.uniform(0.5, 1.5) for _ in range(len(recommendations))]
        
        return recommendations.sort_values(by='recommendation_score', ascending=False)
    return recommendations

# --- 3. Real-time Inventory Management ---
class InventoryManager:
    def __init__(self, initial_stock):
        """
        initial_stock format: {'product_id': {'stock': X, 'max_stock': Y}}
        """
        self.inventory = initial_stock
        self.reorder_threshold = 20
        self.reorder_amount = 50
        
    def process_order(self, product_id, quantity):
        if product_id not in self.inventory:
            print(f"Product {product_id} not found.")
            return False
            
        current_stock = self.inventory[product_id]['stock']
        if current_stock >= quantity:
            self.inventory[product_id]['stock'] -= quantity
            print(f"[Order Processed] {quantity}x {product_id}. Remaining stock: {self.inventory[product_id]['stock']}")
            self._check_reorder_level(product_id)
            return True
        else:
            print(f"[Order Failed] {product_id}: Insufficient stock (Requested: {quantity}, Available: {current_stock})")
            return False
            
    def _check_reorder_level(self, product_id):
        if self.inventory[product_id]['stock'] <= self.reorder_threshold:
            print(f"*** ALERT: Stock for {product_id} is low ({self.inventory[product_id]['stock']}). Initiating reorder of {self.reorder_amount} units. ***")
            # Simulate replenishment
            self.inventory[product_id]['stock'] += self.reorder_amount
            print(f"*** REPLENISHED: {product_id} stock is now {self.inventory[product_id]['stock']} ***")

def main():
    print("=== Online Retail AI System Initialization ===\n")
    
    # Mock Data
    products_data = {
        'product_id': ['P001', 'P002', 'P003', 'P004', 'P005'],
        'name': ['Laptop', 'Smartphone', 'Headphones', 'Smartwatch', 'Tablet'],
        'category': ['Electronics', 'Electronics', 'Accessories', 'Accessories', 'Electronics'],
        'base_price': [1200.0, 800.0, 150.0, 250.0, 600.0]
    }
    products_df = pd.DataFrame(products_data)
    
    inventory_data = {
        'P001': {'stock': 50, 'max_stock': 100},
        'P002': {'stock': 15, 'max_stock': 100},  # Already low stock
        'P003': {'stock': 85, 'max_stock': 100},
        'P004': {'stock': 30, 'max_stock': 50},
        'P005': {'stock': 10, 'max_stock': 50}   # Already below threshold
    }
    
    print("1. Testing Dynamic Pricing Strategies")
    print("-" * 50)
    for index, row in products_df.iterrows():
        pid = row['product_id']
        current_inv = inventory_data[pid]['stock']
        max_inv = inventory_data[pid]['max_stock']
        demand = random.uniform(0.5, 1.8) # Mock demand
        competitor = row['base_price'] * random.uniform(0.8, 1.2) # Mock competitor price
        
        dynamic_price = calculate_dynamic_price(
            row['base_price'], demand, competitor, current_inv, max_inv
        )
        print(f"Product: {row['name']} (Base: ${row['base_price']})")
        print(f"  - Demand Factor: {demand:.2f}, Inventory: {current_inv}/{max_inv}, Competitor: ${competitor:.2f}")
        print(f"  -> Optimized Dynamic Price: ${dynamic_price:.2f}\n")
        
    print("2. Testing Personalized Recommendations")
    print("-" * 50)
    user_profile = {
        'user_id': 'U1001',
        'preferred_categories': ['Accessories', 'Electronics'],
        'past_purchases': ['P001', 'P003'] # Already bought Laptop and Headphones
    }
    print(f"User Profile: Preferred={user_profile['preferred_categories']}, Past Purchases={user_profile['past_purchases']}")
    recs = get_personalized_recommendations(user_profile, products_df)
    print("Recommended Products for User U1001:")
    for _, row in recs.head(2).iterrows(): # Top 2 recommendations
        print(f"  - {row['name']} (${row['base_price']}) in category '{row['category']}'")
        
    print("\n3. Testing Real-time Inventory Management")
    print("-" * 50)
    inv_manager = InventoryManager(inventory_data)
    
    # Simulate some orders
    orders = [
        ('P001', 5),
        ('P004', 15), # 30 - 15 = 15 -> reorder!
        ('P005', 12)  # Request 12, current 10 -> Fail
    ]
    
    for pid, qty in orders:
        print(f"\nProcessing Order: {qty} units of {pid}")
        inv_manager.process_order(pid, qty)
        time.sleep(0.5)
        
    print("\n=== End of Execution ===")

if __name__ == "__main__":
    main()
