// DORSEY Boutique - JavaScript Principal
document.addEventListener('DOMContentLoaded', function() {
    
    // Animation au scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in');
            }
        });
    }, observerOptions);
    
    // Observer les sections
    document.querySelectorAll('section').forEach(section => {
        observer.observe(section);
    });
    
    // Smooth scroll pour les liens
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Gestion du panier
    let cartCount = 0;
    
    window.addToCart = function(productId) {
        cartCount++;
        updateCartBadge();
        
        // Animation de confirmation
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = '✓ Ajouté';
        btn.disabled = true;
        
        setTimeout(() => {
            btn.textContent = originalText;
            btn.disabled = false;
        }, 2000);
        
        // Notification
        showNotification('Produit ajouté au panier !', 'success');
    };
    
    function updateCartBadge() {
        const cartLinks = document.querySelectorAll('a[href*="cart"]');
        cartLinks.forEach(link => {
            if (link.textContent.includes('Panier')) {
                link.innerHTML = `🛒 Panier ${cartCount > 0 ? '(' + cartCount + ')' : ''}`;
            }
        });
    }
    
    // Système de notifications
    function showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success'  '#28a745' : '#dc3545'};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 9999;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
    
    // Animations CSS
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
        
        .animate-fade-in {
            animation: fadeIn 0.8s ease-out forwards;
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    `;
    document.head.appendChild(style);
    
    // Gestion du formulaire de contact
    const contactForm = document.querySelector('form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            showNotification('Message envoyé avec succès ! Nous vous répondrons bientôt.', 'success');
            this.reset();
        });
    }
    
    console.log('DORSEY Boutique - JavaScript chargé avec succès');
});
