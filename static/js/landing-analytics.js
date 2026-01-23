/**
 * Sistema de Analytics para Landing Page do Gestto
 * Rastreia eventos de usuário e envia para Google Analytics e backend Django
 */

(function() {
    'use strict';
    
    // Configuração
    const TRACK_ENDPOINT = '/api/track-event/';
    const CSRF_TOKEN = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                       document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '';
    
    // Estado do rastreamento
    const state = {
        scrollDepths: new Set(),
        sectionTimes: {},
        currentSection: null,
        sectionStartTime: null,
    };
    
    /**
     * Envia evento para Google Analytics (se disponível)
     */
    function sendToGA(eventName, eventParams = {}) {
        if (typeof gtag === 'function') {
            gtag('event', eventName, eventParams);
        }
    }
    
    /**
     * Envia evento para backend Django
     */
    function sendToBackend(eventType, eventData = {}) {
        fetch(TRACK_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': CSRF_TOKEN,
            },
            body: JSON.stringify({
                event_type: eventType,
                event_data: eventData,
                page_url: window.location.href,
            }),
        }).catch(err => console.error('Erro ao enviar evento:', err));
    }
    
    /**
     * Rastreia evento (envia para GA e backend)
     */
    function trackEvent(eventName, eventType, eventData = {}) {
        sendToGA(eventName, eventData);
        sendToBackend(eventType, eventData);
    }
    
    /**
     * Rastreia profundidade de scroll
     */
    function trackScrollDepth() {
        const scrollPercent = Math.round(
            (window.scrollY + window.innerHeight) / document.documentElement.scrollHeight * 100
        );
        
        const depths = [25, 50, 75, 100];
        depths.forEach(depth => {
            if (scrollPercent >= depth && !state.scrollDepths.has(depth)) {
                state.scrollDepths.add(depth);
                trackEvent(
                    'scroll_depth',
                    'scroll_depth',
                    { depth, page: window.location.pathname }
                );
            }
        });
    }
    
    /**
     * Detecta seção visível na tela
     */
    function getCurrentSection() {
        const sections = document.querySelectorAll('section[id]');
        let currentSection = null;
        
        sections.forEach(section => {
            const rect = section.getBoundingClientRect();
            if (rect.top <= window.innerHeight / 2 && rect.bottom >= window.innerHeight / 2) {
                currentSection = section.id;
            }
        });
        
        return currentSection;
    }
    
    /**
     * Rastreia tempo em cada seção
     */
    function trackSectionTime() {
        const section = getCurrentSection();
        
        if (section && section !== state.currentSection) {
            // Registrar tempo da seção anterior
            if (state.currentSection && state.sectionStartTime) {
                const timeSpent = Math.round((Date.now() - state.sectionStartTime) / 1000);
                if (timeSpent > 2) {  // Apenas se passou mais de 2 segundos
                    trackEvent(
                        'section_time',
                        'time_on_section',
                        { section: state.currentSection, time_seconds: timeSpent }
                    );
                }
            }
            
            // Iniciar nova seção
            state.currentSection = section;
            state.sectionStartTime = Date.now();
            
            // Rastrear visualização da seção
            trackEvent(
                'section_view',
                'section_view',
                { section }
            );
        }
    }
    
    /**
     * Rastreia cliques em CTAs
     */
    function setupCTATracking() {
        // Botões "Começar Grátis" e "Participar do Beta"
        document.querySelectorAll('a[href*="cadastro"], .btn-primary, .btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                const ctaName = this.textContent.trim() || 'CTA';
                const href = this.getAttribute('href') || '';
                
                trackEvent(
                    'cta_click',
                    'click_cta',
                    { cta_name: ctaName, href }
                );
            });
        });
    }
    
    /**
     * Rastreia cliques em planos
     */
    function setupPlanTracking() {
        document.querySelectorAll('.pricing-card-home, .btn-plan-home').forEach(card => {
            card.addEventListener('click', function(e) {
                const planName = this.querySelector('h3')?.textContent || 
                                this.closest('.pricing-card-home')?.querySelector('h3')?.textContent || 
                                'Plano';
                
                trackEvent(
                    'plan_click',
                    'plan_click',
                    { plan: planName.trim() }
                );
            });
        });
    }
    
    /**
     * Rastreia abertura de FAQs
     */
    function setupFAQTracking() {
        document.querySelectorAll('.faq-question').forEach(question => {
            question.addEventListener('click', function() {
                const questionText = this.textContent.replace('+', '').trim();
                
                trackEvent(
                    'faq_open',
                    'faq_open',
                    { question: questionText }
                );
            });
        });
    }
    
    /**
     * Rastreia clique no WhatsApp
     */
    function setupWhatsAppTracking() {
        document.querySelectorAll('a[href*="wa.me"], .whatsapp-button').forEach(link => {
            link.addEventListener('click', function() {
                trackEvent(
                    'whatsapp_click',
                    'whatsapp_click',
                    { source: 'floating_button' }
                );
            });
        });
    }
    
    /**
     * Rastreia cliques em links de contato
     */
    function setupContactTracking() {
        document.querySelectorAll('a[href^="mailto:"], a[href^="tel:"]').forEach(link => {
            link.addEventListener('click', function() {
                const type = this.href.startsWith('mailto:') ? 'email' : 'phone';
                const value = this.href.replace(/^(mailto:|tel:)/, '');
                
                trackEvent(
                    'contact_click',
                    'contact_click',
                    { type, value }
                );
            });
        });
    }
    
    /**
     * Rastreia cliques no menu
     */
    function setupMenuTracking() {
        document.querySelectorAll('nav a[href^="#"], nav a[href*="#"]').forEach(link => {
            link.addEventListener('click', function() {
                const section = this.getAttribute('href').replace(/^.*#/, '');
                
                trackEvent(
                    'menu_click',
                    'menu_click',
                    { section }
                );
            });
        });
    }
    
    /**
     * Inicializa todos os rastreamentos
     */
    function init() {
        // Rastreamento de scroll
        let scrollTimeout;
        window.addEventListener('scroll', function() {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                trackScrollDepth();
                trackSectionTime();
            }, 100);
        }, { passive: true });
        
        // Rastreamento de cliques
        setupCTATracking();
        setupPlanTracking();
        setupFAQTracking();
        setupWhatsAppTracking();
        setupContactTracking();
        setupMenuTracking();
        
        // Rastrear seção inicial
        setTimeout(trackSectionTime, 1000);
        
        // Rastrear tempo total na página ao sair
        window.addEventListener('beforeunload', function() {
            if (state.currentSection && state.sectionStartTime) {
                const timeSpent = Math.round((Date.now() - state.sectionStartTime) / 1000);
                if (timeSpent > 2) {
                    sendToBackend('time_on_section', {
                        section: state.currentSection,
                        time_seconds: timeSpent
                    });
                }
            }
        });
    }
    
    // Inicializar quando DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
