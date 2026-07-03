import requests
from typing import Dict, Any
from apps.products.models import ProductCode
from .models import GlobalProduct

class ProductLookupService:
    @staticmethod
    def lookup_by_barcode(barcode: str, store_id: str) -> Dict[str, Any]:
        # 1. Buscar en Product actual por barcode y store_id
        store_code = ProductCode.objects.filter(
            product__store_id=store_id,
            code=barcode
        ).select_related('product').first()

        if store_code:
            product = store_code.product
            return {
                "source": "store",
                "product": {
                    "id": str(product.id),
                    "name": product.name,
                    "barcode": barcode,
                    "image_url": product.image_url,
                    "base_cost": str(product.base_cost),
                    "sale_price": str(product.sale_price)
                }
            }
        
        # 2. Buscar en GlobalProduct
        global_product = GlobalProduct.objects.filter(barcode=barcode).first()
        if global_product:
            return {
                "source": "global",
                "product": {
                    "id": str(global_product.id),
                    "name": global_product.name,
                    "brand": global_product.brand,
                    "category": global_product.category,
                    "image_url": global_product.image_url,
                    "barcode": global_product.barcode
                }
            }

        # 3. Buscar en OpenFoodFacts
        try:
            url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
            headers = {"User-Agent": "NuraxSmartInventory - Web - Version 1.0 - nurax.com"}
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == 1:
                    prod_data = data.get("product", {})
                    name = prod_data.get("product_name", "")
                    brand = prod_data.get("brands", "")
                    category = prod_data.get("categories", "")
                    image_url = prod_data.get("image_url", "")
                    
                    if not name:
                        name = brand if brand else "Producto Desconocido"
                        
                    if name:
                        new_global_product = GlobalProduct.objects.create(
                            barcode=barcode,
                            name=name[:255],
                            brand=brand[:255] if brand else "",
                            category=category[:255] if category else "",
                            image_url=image_url[:500] if image_url else ""
                        )
                        return {
                            "source": "openfoodfacts",
                            "product": {
                                "id": str(new_global_product.id),
                                "name": new_global_product.name,
                                "brand": new_global_product.brand,
                                "category": new_global_product.category,
                                "image_url": new_global_product.image_url,
                                "barcode": new_global_product.barcode
                            }
                        }
        except requests.RequestException:
            pass
        
        return {
            "source": "not_found",
            "product": None
        }
