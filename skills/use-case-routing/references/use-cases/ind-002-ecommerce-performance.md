---
id: ind-002
name: Secure and accelerate ecommerce
category: industry-verticals
description: Deliver fast global storefronts with bot protection, PCI compliance, and traffic surge management.
products: [CDN, WAF, Bot Management, Waiting Room, DDoS Protection]
default_path: ecommerce-performance
aliases:
  - Ecommerce security and performance
  - Online store optimization
  - Retail site protection
keywords:
  - "speed up checkout"
  - "scalper bots"
  - "inventory hoarding"
  - "flash sale traffic"
  - "Black Friday traffic"
  - "PCI DSS"
  - "Shopify alternative protection"
  - "Magento performance"
  - "abandoned cart speed"
related:
  - sec-003
  - perf-016
  - perf-001
  - sec-006
---

# Secure and accelerate ecommerce

## Ask first

**What is your primary ecommerce concern?**
- Page load speed and conversion optimization → ecommerce-performance
- Bot attacks (scalping, scraping, credential stuffing) → ecommerce-bot-protection
- Flash sale or traffic surge management → flash-sale
- PCI DSS compliance → ecommerce-bot-protection (rate limiting and WAF coverage; pair with related compliance use cases)
- Multiple concerns → walk ecommerce-performance, ecommerce-bot-protection, and flash-sale in sequence

## Paths

### ecommerce-performance (default)

Accelerate the storefront:

- Configure CDN caching for product images, CSS, and JS globally
- Enable Tiered Cache for higher hit ratios
- Use Cloudflare Images to optimize product images dynamically
- Enable Argo Smart Routing for faster checkout paths

### ecommerce-bot-protection

Stop scalpers, scrapers, and credential stuffers:

1. Enable Bot Analytics to profile traffic on product and checkout pages
2. Create WAF custom rules based on bot scores to block automated purchasing and scraping
3. Add Turnstile to checkout and login flows
4. Add WAF rate limiting rules for add-to-cart and checkout endpoints

### flash-sale

Manage traffic surges and flash sales:

1. Create a Waiting Room for the sale landing page
2. Set user thresholds based on origin capacity
3. Pre-cache all static assets in the CDN before the sale
4. Configure Load Balancing failover for origin resilience

## Hand off

For implementation, retrieve from Cloudflare docs:
https://developers.cloudflare.com/cache/, /waf/, /bot-management/,
/waiting-room/, /ddos-protection/, /images/, /argo-smart-routing/,
/turnstile/, /load-balancing/.
Browse https://github.com/cloudflare/skills/tree/main/skills for any
matching builder skills.
