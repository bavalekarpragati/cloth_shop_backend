from shop.models import Category, Product

def cat(name):
    return Category.objects.get(name=name)

# 1. Re-file the products still sitting in "Ladies Wear"
old = Category.objects.get(name="Ladies Wear")
moves = {"feather": "Casual Tops", "duptta": "Dupatta Matching"}

for p in Product.objects.filter(category=old):
    moved = False
    for key, target in moves.items():
        if key in p.name.lower():
            p.category = cat(target)
            p.save()
            print("Moved:", p.name, "->", target)
            moved = True
    if not moved:
        print("Left in Ladies Wear (no rule for it):", p.name)

# 2. Short-kurti is a type of kurti
sk = Category.objects.get(name="Short-kurti")
sk.parent = cat("Kurtis")
sk.save()

# 3. Delete the old categories, but only if they are truly empty
for name in ["Ladies Wear", "Kids Wear"]:
    c = Category.objects.get(name=name)
    if c.products.exists() or c.subcategories.exists():
        print("NOT deleted (still has products or subcategories):", name)
    else:
        c.delete()
        print("Deleted:", name)
        