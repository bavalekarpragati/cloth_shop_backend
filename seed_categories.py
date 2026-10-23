from shop.models import Category

def add(name, parent=None):
    obj, _ = Category.objects.get_or_create(name=name)
    obj.parent = parent
    obj.save()
    return obj

# ---- Traditional ----
trad = add("Traditional")
add("Traditional Dresses", trad)
add("Kurtis", trad)
sarees = add("Sarees", trad)
add("Heavy Work Sarees", sarees)
add("Catalog Sarees", sarees)

# ---- Casual ----
casual = add("Casual")
for n in ["Casual Tops", "Jeans Tops", "Jeans", "Dresses",
          "One Piece Short", "One Piece Long", "Long Skirts"]:
    add(n, casual)

# ---- Matching ----
matching = add("Matching")
for n in ["Dupatta Matching", "Leggings", "Plazzo", "Pants Matching"]:
    add(n, matching)

# ---- Kids ----
kids = add("Kids")
girls = add("Girls", kids)
for n in ["Girls Dresses", "Ghagras", "Gharara Dresses", "Patiyala Dress",
          "Girls One Piece Short", "Girls One Piece Long", "Skirt Top Short",
          "Frocks", "Pant and Top", "Catalog Pieces"]:
    add(n, girls)

boys = add("Boys", kids)
for n in ["Kurta Pajama", "Boys Jeans", "T-Shirts", "Shirts", "Jacket Set", "Suits"]:
    add(n, boys)

print("Done:", Category.objects.count(), "categories")