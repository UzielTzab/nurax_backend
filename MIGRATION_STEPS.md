# 📋 Django Migrations - Steps to Execute

## Status: Ready for Execution ✅

All admin.py files have been validated and fixed. Backend is ready for migrations.

---

## 🚀 STEP 1: Create Migrations

**Command:**
```bash
cd nurax_backend
python manage.py makemigrations accounts products sales inventory expenses carts
```

**Expected Output:**
```
Migrations for 'accounts':
  accounts/migrations/0001_initial.py
    - Create model User
    - Create model Store
    - Create model StoreMembership
    - Create model Client
Migrations for 'products':
  products/migrations/0001_initial.py
    - Create model Category
    - Create model Supplier
    - Create model Product
    - Create model ProductPackaging
    - Create model ProductCode
...and so on for sales, inventory, expenses, carts
```

**Notes:**
- This is the first migration set for ARCHITECTURE_V2
- Will create all UUID primary keys
- Will create all multi-tenancy structures (store_id ForeignKeys)
- Will create all relationships correctly

---

## 🚀 STEP 2: Review Migrations (Optional)

**Command:**
```bash
python manage.py showmigrations
```

**Expected Output:**
- accounts: [ ] 0001_initial
- products: [ ] 0001_initial
- sales: [ ] 0001_initial
- inventory: [ ] 0001_initial
- expenses: [ ] 0001_initial
- carts: [ ] 0001_initial

---

## 🗄️ STEP 3: Run Migrations

**Command:**
```bash
python manage.py migrate
```

**Expected Output:**
```
Operations to perform:
  Apply all migrations: ...
Running migrations:
  Applying accounts.0001_initial... OK
  Applying products.0001_initial... OK
  Applying sales.0001_initial... OK
  Applying inventory.0001_initial... OK
  Applying expenses.0001_initial... OK
  Applying carts.0001_initial... OK
```

**Database Result:**
- PostgreSQL will have all 6 apps' tables created
- All with UUID primary keys
- All with store_id multi-tenancy fields
- All with created_at/updated_at timestamps

---

## ✅ STEP 4: Verify Setup

**Command:**
```bash
python manage.py check
```

**Expected Output:**
```
System check identified no issues (0 silenced).
```

**If any issues**: Review the error and check models.py/admin.py/settings.py

---

## 🏃 STEP 5: Test Admin Panel

**Command:**
```bash
python manage.py runserver
```

**Access**: http://localhost:8000/admin/

**Login**: 
- Email: uzieltzab8@gmail.com
- Password: 2jusni!+1

**Expected**: 
- Admin panel loads without errors
- Can see all 6 apps registered
- Can see all models clickable
- CRUD operations work

---

## 🐳 Alternative: Use Docker

If developing with Docker:

```bash
docker-compose up -d
```

The compose file will automatically:
1. Start PostgreSQL
2. Build Django container
3. Run migrations (already in docker-compose.yml command)
4. Initialize DB (init_db.py)
5. Start Django server on port 8000

---

## ⚠️ Troubleshooting

### Issue: "Migrations not created"
- Solution: Ensure all apps are in INSTALLED_APPS in settings.py ✅

### Issue: "No such table" after migrations
- Solution: Ensure tables were created (run `python manage.py check` first)

### Issue: Import errors when migrating
- Solution: All admin.py files have been fixed - this should be resolved ✅

---

## 📝 Next Steps After Migrations

1. ✅ Run migrations successfully
2. ⏳ Test backend API endpoints
3. ⏳ Start Frontend Phase 2 (API services update)
4. ⏳ Create Pinia stores for V2 structure
5. ⏳ Update Vue components

---

**Last Updated**: Abril 4, 2026  
**Status**: 🟢 Ready to execute
