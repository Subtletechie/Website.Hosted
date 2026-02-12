// ============================================================
//  SUBTLETECH CONTENT FILE
//  ========================
//  This is the ONLY file you need to edit to update your site.
//  Change any text, add blog posts, update testimonials, etc.
//  Then push to GitHub and Vercel auto-deploys in ~30 seconds.
//
//  Contact: subtletechie@outlook.com
// ============================================================

// ─── HOMEPAGE HERO ───────────────────────────────
export const hero = {
  title: "Cloud Security Engineer",
  titleAccent: "Consultant & Educator",
  subtitle:
    "Helping organizations secure their cloud and AI environments through expert consulting, hands-on training, and battle-tested strategies.",
};

// ─── STATS (shown on homepage) ───────────────────
export const stats = [
  { num: "500+", label: "Hours of Mentorship" },
  { num: "50+", label: "Cloud Assessments" },
  { num: "3", label: "Cloud Platforms" },
  { num: "12+", label: "Industry Certifications" },
];

// ─── ABOUT PAGE ──────────────────────────────────
export const about = {
  headline:
    "Hi, I'm the cloud security engineer who believes security doesn't have to be intimidating.",

  // Use \n\n for paragraph breaks
  bio: `I started my career in IT support — troubleshooting tickets and resetting passwords. But I kept getting pulled toward the security side of things: why are we configured this way? What happens if someone gets in? How do we actually protect this stuff?

That curiosity led me deep into cloud security, where I discovered my two passions: solving complex multi-cloud security challenges and making those solutions understandable for everyone. I believe the biggest security risk isn't sophisticated attacks — it's the gap between what teams know and what they need to know.

Today, I help organizations secure their cloud and AI environments through consulting, and I help individuals break into cloud security through education and mentorship. Whether I'm working with a Fortune 500's security team or mentoring someone making their first career pivot, I bring the same philosophy: security should be practical, understandable, and empowering.`,

  expertise: [
    "Multi-Cloud Security (AWS, Azure, GCP)",
    "RBAC & IAM Architecture",
    "AI/ML Security",
    "Security Architecture",
    "Cloud Compliance",
    "Zero Trust Design",
    "Incident Response",
    "Security Education",
  ],

  certifications: [
    "AWS Solutions Architect – Professional",
    "Azure Security Engineer Associate",
    "GCP Professional Cloud Security Engineer",
    "CompTIA Security+",
    "Certified Cloud Security Professional (CCSP)",
    "Certified Information Systems Security Professional (CISSP)",
  ],
};

// ─── TESTIMONIALS ────────────────────────────────
// To add a testimonial later, just add an entry like:
// { name: "Name", role: "Their Title", text: "What they said." },
export const testimonials = [];

// ─── CASE STUDIES (Consulting page) ──────────────
export const caseStudies = [
  {
    title: "FinTech Startup — Multi-Cloud Hardening",
    result: "92% reduction in critical findings",
    desc: "Assessed and remediated security posture across AWS and Azure before Series B due diligence. Implemented IAM governance and automated compliance monitoring.",
  },
  {
    title: "Healthcare SaaS — HIPAA Cloud Compliance",
    result: "Full HIPAA compliance in 8 weeks",
    desc: "Designed and deployed HIPAA-compliant architecture on AWS including encryption, access controls, audit logging, and incident response procedures.",
  },
  {
    title: "Enterprise — AI Security Program",
    result: "Zero AI-related incidents post-engagement",
    desc: "Built an AI security governance framework covering model inventory, risk assessment, and secure deployment pipelines for a Fortune 500 company's ML operations.",
  },
];

// ─── BLOG POSTS ──────────────────────────────────
// To add a new post: copy any block below, paste it at the TOP
// of the array (newest first), and fill in your content.
//
// Available tags: "Cloud Security", "Azure", "AWS", "GCP",
//                 "AI Security", "RBAC", "Career"
//
// Set published: false to hide a post (draft mode)
//
// THUMBNAILS: Add your image to the /public/thumbnails/ folder
// in GitHub, then set the image field to "/thumbnails/your-image.png"
// If you don't have a thumbnail, just leave image as "" and
// the card will show without one.
export const blogPosts = [
  {
    id: "b9",
    title: "ICS Security: The Goldmine Niche in Cybersecurity",
    excerpt:
      "Industrial control systems are high stakes — they keep civilization running. Here's why ICS security professionals out-earn their peers by 15-30%, and why this niche is worth your attention.",
    image: "/thumbnails/ics-security-thumbnail.png",
    date: "Feb 11, 2026",
    read: "4 min",
    tags: ["Cloud Security", "Career"],
    published: true,
  },
  {
    id: "b1",
    title: "Why Multi-Cloud Security Isn't Optional Anymore",
    excerpt:
      "As organizations spread workloads across Azure, AWS, and GCP, unified security policies become critical. Here's how to build a strategy that scales.",
    image: "",
    date: "Jan 28, 2026",
    read: "6 min",
    tags: ["Cloud Security", "AWS", "Azure"],
    published: true,
  },
  {
    id: "b2",
    title: "The RBAC Pitfalls That Leave Your Cloud Exposed",
    excerpt:
      "Role-Based Access Control seems straightforward—until misconfigurations create privilege escalation paths. Learn the patterns attackers exploit.",
    image: "",
    date: "Jan 15, 2026",
    read: "8 min",
    tags: ["RBAC", "Cloud Security"],
    published: true,
  },
  {
    id: "b3",
    title: "AI Model Security: Protecting Your ML Pipeline",
    excerpt:
      "From data poisoning to model theft, AI/ML systems face unique threats. A practical guide to securing every stage of the pipeline.",
    image: "",
    date: "Jan 5, 2026",
    read: "10 min",
    tags: ["AI Security", "Cloud Security"],
    published: true,
  },
  {
    id: "b4",
    title: "Azure Sentinel vs. AWS Security Hub: An Honest Comparison",
    excerpt:
      "Both platforms promise unified security visibility. After deploying both in production, here's what actually matters for your SOC team.",
    image: "",
    date: "Dec 20, 2025",
    read: "7 min",
    tags: ["Azure", "AWS", "Cloud Security"],
    published: true,
  },
  {
    id: "b5",
    title: "From Help Desk to Cloud Security: My Career Path",
    excerpt:
      "I didn't start in security. Here's the honest story of how I pivoted from IT support to cloud security consulting—and what I'd do differently.",
    image: "",
    date: "Dec 8, 2025",
    read: "5 min",
    tags: ["Career"],
    published: true,
  },
  {
    id: "b6",
    title: "GCP IAM Best Practices for Enterprise Teams",
    excerpt:
      "Google Cloud's IAM model differs from AWS and Azure in subtle but important ways. Master these patterns to avoid common misconfigurations.",
    image: "",
    date: "Nov 25, 2025",
    read: "9 min",
    tags: ["GCP", "RBAC"],
    published: true,
  },
  {
    id: "b7",
    title: "Securing LLM Applications in Production",
    excerpt:
      "Large language models introduce novel attack surfaces. Prompt injection, data leakage, and model manipulation require new defensive approaches.",
    image: "",
    date: "Nov 12, 2025",
    read: "11 min",
    tags: ["AI Security"],
    published: true,
  },
  {
    id: "b8",
    title: "Zero Trust Architecture: Beyond the Buzzword",
    excerpt:
      "Everyone talks about Zero Trust, but few implement it correctly. Here's a practical framework for cloud-native Zero Trust that actually works.",
    image: "",
    date: "Oct 30, 2025",
    read: "8 min",
    tags: ["Cloud Security", "AWS", "Azure", "GCP"],
    published: true,
  },
];

// ─── SOCIAL LINKS ────────────────────────────────
// Update the url fields with your actual profile links
export const socials = [
  {
    type: "discord",
    name: "Discord",
    desc: "Join SubtleNation — our cloud security community.",
    cta: "Join Community",
    url: "https://discord.gg/wvYBGujv",
    color: "#5865F2",
  },
  {
    type: "twitter",
    name: "Twitter / X",
    desc: "Quick takes on cloud security news and threads.",
    cta: "Follow @subtletechie",
    url: "https://x.com/subtletechie",
    color: "#1DA1F2",
  },
  {
    type: "linkedin",
    name: "LinkedIn",
    desc: "Long-form posts about cloud security strategy and career advice.",
    cta: "Connect",
    url: "https://www.linkedin.com/in/francismaduka",
    color: "#0A66C2",
  },
  {
    type: "instagram",
    name: "Instagram",
    desc: "Behind-the-scenes of cloud security life, tips, and quick visual guides.",
    cta: "Follow Me",
    url: "https://www.instagram.com/subtletechie/",
    color: "#E4405F",
  },
  {
    type: "tiktok",
    name: "TikTok",
    desc: "Bite-sized cloud security tips, career advice, and tech breakdowns.",
    cta: "Follow Me",
    url: "https://www.tiktok.com/@thesubtletechie",
    color: "#00F2EA",
  },
  {
    type: "youtube",
    name: "YouTube",
    desc: "In-depth tutorials and cloud security walkthroughs.",
    cta: "Subscribe",
    url: "https://www.youtube.com/@subtle-techie",
    color: "#FF0000",
  },
];

// ─── SITE SETTINGS ───────────────────────────────
export const siteSettings = {
  email: "subtletechie@outlook.com",
  siteName: "SubtleTech",
  tagline: "Cloud Security · AI Security · Education",
  copyright: "© 2026 SubtleTech Consulting. All rights reserved.",
};
