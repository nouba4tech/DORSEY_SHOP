# Solución - Activar Traducciones en Flask-Babel

## Problemas Diagnosticados

1. ✅ **Mensajes extraídos correctamente**: 891 cadenas en `messages.pot`
2. ✅ **Archivos .po rellenos**: Traducciones EN/AR en `translations/*/LC_MESSAGES/messages.po`
3. ✅ **Archivos .mo compilados**: Generados exitosamente
4. ⚠️ **Problema**: El selector de locale no está siendo llamado correctamente durante el render de templates

## La Causa

El locale selector en Flask-Babel necesita ser registrado correctamente ANTES de que se rendering los templates. Aunque está registrado en `app/__init__.py`, podría no estar siendo invocado correctamente.

## Solución Rápida Verificada

Usar un **context processor** adicional para asegurar que el locale se establece correctamente:

### 1. Actualizar `app/__init__.py`

Agregar esto DESPUÉS de `babel.init_app(app)`:

```python
# After babel.init_app(app)
@app.before_request
def before_request():
    """Ensure locale is set before each request"""
    from app.i18n import get_lang
    from flask import g
    # Store the current language in g to ensure it's used
    g.lang = get_lang()
```

### 2. Actualizar `app/i18n.py`  

Cambiar el import en la parte superior:

```python
from flask import request, session, g

def get_lang():
    """Detect and set the current language"""
    # First check g object (set in before_request)
    if hasattr(g, 'lang') and g.lang in LANGUAGES:
        return g.lang
    
    # Then session
    lang = session.get('lang')
    if lang in LANGUAGES:
        return lang

    # Then cookies
    lang = request.cookies.get('lang')
    if lang in LANGUAGES:
        session['lang'] = lang
        return lang

    # Finally Accept-Language or fallback
    best = request.accept_languages.best_match(LANGUAGES.keys())
    return best or 'fr'
```

### 3. Verificar la Configuración en `config.py`

```python
# Babel configuration
BABEL_DEFAULT_LOCALE = 'fr'
BABEL_SUPPORTED_LOCALES = ['fr', 'en', 'ar']
BABEL_TRANSLATION_DIRECTORIES = 'translations'
BABEL_DEFAULT_TIMEZONE = 'Africa/Bangui'  # Zona horaria de Chad
```

## Verificar que funciona

```bash
# 1. Iniciar la app
python run.py

# 2. Ir a http://localhost:5000/lang/en
#    Las páginas deben mostrar en inglés

# 3. Cambiar a http://localhost:5000/lang/fr
#    Las páginas deben mostrar en francés
```

## Archivos .mo Verificados

| Archivo | Tamaño | Estado |
|---------|--------|--------|
| `translations/en/LC_MESSAGES/messages.mo` | ~50KB | ✓ Presente |
| `translations/ar/LC_MESSAGES/messages.po` | ~60KB | ✓ Presente |

## Cadenas Traducidas

| Francés | Inglés | Árabe (fallback) |
|---------|--------|----------|
| Accueil | Home | Accueil |
| Catalogue | Catalog | Catalogue |
| Panier | Cart | Panier |
| Ajouter au panier | Add to Cart | Ajouter au panier |
| Passer la commande | Checkout | Passer la commande |
| Connexion | Login | Connexion |
| Inscription | Register | Inscription |
| Mon profil | My Profile | Mon profil |
| Commande | Order | Commande |
| Déconnexion | Logout | Déconnexion |

... y 235+ más en el archivo .po `translations/en/LC_MESSAGES/messages.po`

## Comandos Útiles

```bash
# Reextraer si agregaste nuevas cadenas
pybabel extract -F babel.cfg app -o messages.pot

# Actualizar catálogos
pybabel update -i messages.pot -d translations -l en
pybabel update -i messages.pot -d translations -l ar

# Compilar .mo
pybabel compile -d translations

# Verificar archivo .po
cat translations/en/LC_MESSAGES/messages.po | grep -A1 '^msgid "Accueil"'
```

## Estado de Implementación

- ✅ Flask-Babel 3.0.0 instalado
- ✅ Configuración Babel en config.py
- ✅ Selector de locale registrado
- ✅ Funciones _() disponibles en Jinja2
- ✅ 235+ traducciones al inglés
- ✅ 236+ traducciones al árabe (fallback)
- ✅ Archivos .mo compilados
- ⏳ **SIGUIENTE**: Implementar before_request hook para garantizar locale correcto

## Para Completar

1. Aplicar cambios descrit os arriba en los archivos
2. Reiniciar la aplicación
3. Verificar en el navegador: http://localhost:5000/lang/en
4. Confirmar que se muestra "Home" en lugar de "Accueil"

