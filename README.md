Plan: Host Website on GitHub Pages with Custom Domain

  Prerequisites

  - The repository is already on GitHub (jacobbogolia/ResolvedLawGroupWebsite)
  - You have access to the domain registrar's DNS settings
  - You know the custom domain name (e.g., resolvedlawgroup.com)

  ---
  Step 1: Create a CNAME file in the repository

  Add a file called CNAME (no extension) to the root of the repository containing just the custom domain name. This tells GitHub Pages which domain to use.

  ---
  Step 2: Enable GitHub Pages in repository settings

  1. Go to the repository on GitHub
  2. Navigate to Settings → Pages
  3. Under "Build and deployment":
    - Source: Deploy from a branch
    - Branch: Select main (or no-framework if that's the production branch), folder: / (root)
  4. Under "Custom domain": Enter the domain (e.g., resolvedlawgroup.com)
  5. Click Save

  ---
  Step 3: Configure DNS at the domain registrar

  For an apex domain (e.g., resolvedlawgroup.com):

  Add these A records:
  | Type | Host | Value           |
  |------|------|-----------------|
  | A    | @    | 185.199.108.153 |
  | A    | @    | 185.199.109.153 |
  | A    | @    | 185.199.110.153 |
  | A    | @    | 185.199.111.153 |

  For the www subdomain (recommended):

  Add a CNAME record:
  | Type  | Host | Value                  |
  |-------|------|------------------------|
  | CNAME | www  | jacobbogolia.github.io |

  This ensures both resolvedlawgroup.com and www.resolvedlawgroup.com work.

  ---
  Step 4: Wait for DNS propagation

  DNS changes can take anywhere from a few minutes to 24 hours to propagate.

  ---
  Step 5: Enable HTTPS

  Once DNS is configured and GitHub verifies the domain:
  1. Go back to Settings → Pages
  2. Check Enforce HTTPS (this may take up to 24 hours to become available)

  ---
  Optional: Verify the domain (recommended for security)

  1. Go to GitHub → Settings → Pages → Verified domains
  2. Add the domain and follow the TXT record verification steps

  ---

CHRISTIAN WHADDUP DOE
Buttons that aren't working: 
    1. "Free Consultation" button in the header of the webpage
    2. "Free Consultation" button under the "Let's talk. We can help." on the main page
    3. "About our Company" same section.
    4. "Free Consultation" button in the footer of each page.
 
    
