# API de Configuración de Membresías

## Endpoint de Actualización de Planes

### `POST /api/membership/plans/update/`

Actualiza la configuración de precios de los planes de membresía (Monthly o Annual).

**Requiere**: Usuario autenticado con rol de Administrador

---

## Request

### Headers
```
Content-Type: application/json
Authorization: Session (usuario debe estar autenticado)
```

### Body JSON

```json
{
  "slug": "monthly",           // "monthly" o "annual"
  "price": 29.00,              // Precio base (requerido)
  "original_price": 35.00,     // Precio original para mostrar descuento (opcional)
  "is_active": true            // Estado del plan (opcional, default: true)
}
```

---

## Response

### Success (200 OK)

```json
{
  "success": true,
  "message": "Plan Monthly actualizado correctamente",
  "plan": {
    "id": 1,
    "name": "Monthly",
    "slug": "monthly",
    "price": "29.00",
    "original_price": "35.00",
    "is_active": true,
    "savings": "6.00"
  }
}
```

### Error Responses

**403 Forbidden** - Usuario sin permisos
```json
{
  "error": "No tienes permisos para realizar esta acción"
}
```

**400 Bad Request** - Datos inválidos
```json
{
  "error": "Slug inválido. Debe ser 'monthly' o 'annual'"
}
```

**404 Not Found** - Plan no encontrado
```json
{
  "error": "Plan con slug 'monthly' no encontrado"
}
```

---

## Ejemplos de Uso

### Actualizar Plan Mensual

```bash
curl -X POST http://localhost:8000/api/membership/plans/update/ \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "monthly",
    "price": 29.00,
    "original_price": null,
    "is_active": true
  }'
```

### Actualizar Plan Anual con Descuento

```bash
curl -X POST http://localhost:8000/api/membership/plans/update/ \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "annual",
    "price": 249.00,
    "original_price": 348.00,
    "is_active": true
  }'
```

### Desactivar un Plan

```bash
curl -X POST http://localhost:8000/api/membership/plans/update/ \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "monthly",
    "price": 29.00,
    "is_active": false
  }'
```

---

## Uso desde JavaScript (Frontend)

```javascript
async function updateMembershipPlan(slug, price, originalPrice, isActive) {
  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  
  const response = await fetch('/api/membership/plans/update/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken
    },
    body: JSON.stringify({
      slug: slug,
      price: price,
      original_price: originalPrice,
      is_active: isActive
    })
  });
  
  const data = await response.json();
  
  if (data.success) {
    console.log('Plan actualizado:', data.plan);
    alert(data.message);
  } else {
    console.error('Error:', data.error);
    alert('Error: ' + data.error);
  }
}

// Ejemplo de uso
updateMembershipPlan('annual', 249.00, 348.00, true);
```

---

## Validaciones

1. **Slug**: Debe ser exactamente "monthly" o "annual"
2. **Price**: 
   - Campo requerido
   - Debe ser un número válido
   - No puede ser negativo
3. **Original Price**:
   - Campo opcional
   - Si se proporciona, debe ser un número válido
   - No puede ser negativo
   - Si es null o 0, no se mostrará descuento
4. **Is Active**:
   - Campo opcional (default: true)
   - Controla si el plan está disponible para suscripción

---

## Notas Importantes

- Los cambios se aplican **inmediatamente** en el frontend
- Los usuarios con suscripciones activas **mantienen su precio actual** hasta la renovación
- Solo usuarios con rol ADMIN, staff o superuser pueden usar este endpoint
- El endpoint calcula automáticamente el campo `savings` si hay `original_price`
