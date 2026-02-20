import { useState, useEffect } from "react";
import {
  hero, stats, about, testimonials, caseStudies,
  blogPosts, socials, siteSettings
} from "./content";

// ─── COLORS ──────────────────────────────────────
const C = {
  bg: "#0B1120", bgCard: "#111B2E", bgHover: "#162036",
  bgNav: "rgba(11,17,32,0.95)", accent: "#2563EB", accentH: "#3B82F6",
  glow: "rgba(37,99,235,0.15)", white: "#F1F5F9", muted: "#94A3B8",
  border: "rgba(148,163,184,0.12)", green: "#10B981", purple: "#8B5CF6",
};

const PAGES = ["Home", "Consulting", "Education", "Blog", "About", "Connect"];
const ALL_TAGS = ["Cloud Security", "Azure", "AWS", "GCP", "AI Security", "RBAC", "Career"];

// ─── ICONS ───────────────────────────────────────
const Icons = {
  Shield: () => <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>,
  Cloud: () => <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"/></svg>,
  Brain: () => <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M12 2a7 7 0 0 0-7 7c0 2.38 1.19 4.47 3 5.74V17a2 2 0 0 0 2 2h4a2 2 0 0 0 2-2v-2.26c1.81-1.27 3-3.36 3-5.74a7 7 0 0 0-7-7z"/><line x1="9" y1="21" x2="15" y2="21"/></svg>,
  Book: () => <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>,
  Lock: () => <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>,
  Check: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10B981" strokeWidth="2.5"><polyline points="20 6 9 17 4 12"/></svg>,
  Arrow: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>,
  ArrowLeft: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>,
  Search: () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>,
  Menu: () => <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>,
  X: () => <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>,
  Ext: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>,
  Mail: () => <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>,
  Star: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="#FBBF24" stroke="#FBBF24" strokeWidth="1"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>,
  Clock: () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>,
  Cert: () => <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="12" cy="8" r="6"/><path d="M15.477 12.89L17 22l-5-3-5 3 1.523-9.11"/></svg>,
};

const SocialIcon = ({ type }) => {
  const paths = {
    discord: <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03z" fill="currentColor"/>,
    twitter: <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" fill="currentColor"/>,
    linkedin: <><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452z" fill="currentColor"/></>,
    youtube: <><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814z" fill="currentColor"/><polygon points="9.545,15.568 15.818,12 9.545,8.432" fill="#0B1120"/></>,
    instagram: <><path d="M7.8 2h8.4C19.4 2 22 4.6 22 7.8v8.4a5.8 5.8 0 0 1-5.8 5.8H7.8C4.6 22 2 19.4 2 16.2V7.8A5.8 5.8 0 0 1 7.8 2m-.2 2A3.6 3.6 0 0 0 4 7.6v8.8C4 18.39 5.61 20 7.6 20h8.8a3.6 3.6 0 0 0 3.6-3.6V7.6C20 5.61 18.39 4 16.4 4H7.6m9.65 1.5a1.25 1.25 0 0 1 1.25 1.25A1.25 1.25 0 0 1 17.25 8 1.25 1.25 0 0 1 16 6.75a1.25 1.25 0 0 1 1.25-1.25M12 7a5 5 0 0 1 5 5 5 5 0 0 1-5 5 5 5 0 0 1-5-5 5 5 0 0 1 5-5m0 2a3 3 0 0 0-3 3 3 3 0 0 0 3 3 3 3 0 0 0 3-3 3 3 0 0 0-3-3z" fill="currentColor"/></>,
    tiktok: <><path d="M16.6 5.82s.51.5 0 0A4.278 4.278 0 0 1 15.54 3h-3.09v12.4a2.592 2.592 0 0 1-2.59 2.5c-1.42 0-2.6-1.16-2.6-2.6 0-1.72 1.66-3.01 3.37-2.48V9.66c-3.45-.46-6.47 2.22-6.47 5.64 0 3.33 2.76 5.7 5.69 5.7 3.14 0 5.69-2.55 5.69-5.7V9.01a7.35 7.35 0 0 0 4.3 1.38V7.3s-1.88.09-3.24-1.48z" fill="currentColor"/></>,
  };
  return <svg width="24" height="24" viewBox="0 0 24 24">{paths[type]}</svg>;
};

// ─── SHARED UI ───────────────────────────────────
const Badge = ({ children }) => (
  <span style={{ display: "inline-block", padding: "4px 12px", borderRadius: 20, fontSize: 12, fontWeight: 600, background: C.glow, color: C.accentH, letterSpacing: 0.5 }}>{children}</span>
);

const Btn = ({ children, variant = "primary", onClick, style, type }) => {
  const [h, setH] = useState(false);
  const base = { display: "inline-flex", alignItems: "center", gap: 8, padding: "12px 28px", borderRadius: 10, fontWeight: 600, fontSize: 15, cursor: "pointer", transition: "all 0.25s", border: "none", fontFamily: "inherit" };
  const s = variant === "primary"
    ? { ...base, background: h ? C.accentH : C.accent, color: "#fff", boxShadow: h ? "0 0 24px rgba(37,99,235,0.4)" : "none", transform: h ? "translateY(-1px)" : "none" }
    : { ...base, background: "transparent", color: C.white, border: `1px solid ${C.border}`, ...(h ? { borderColor: C.accent, background: "rgba(37,99,235,0.08)" } : {}) };
  return <button type={type || "button"} style={{ ...s, ...style }} onMouseEnter={() => setH(true)} onMouseLeave={() => setH(false)} onClick={onClick}>{children}</button>;
};

const Card = ({ children, style, hover = true, onClick }) => {
  const [h, setH] = useState(false);
  return (
    <div onClick={onClick} onMouseEnter={() => setH(true)} onMouseLeave={() => setH(false)} style={{
      background: h && hover ? C.bgHover : C.bgCard, border: `1px solid ${h && hover ? "rgba(37,99,235,0.3)" : C.border}`,
      borderRadius: 16, padding: 32, transition: "all 0.3s", transform: h && hover ? "translateY(-4px)" : "none",
      boxShadow: h && hover ? "0 12px 40px rgba(0,0,0,0.3)" : "0 4px 16px rgba(0,0,0,0.15)",
      cursor: onClick ? "pointer" : "default", ...style
    }}>{children}</div>
  );
};

const Sec = ({ children, style }) => (
  <section style={{ padding: "100px 0", maxWidth: 1200, margin: "0 auto", paddingLeft: 24, paddingRight: 24, ...style }}>{children}</section>
);

const STitle = ({ badge, title, subtitle }) => (
  <div style={{ textAlign: "center", marginBottom: 60 }}>
    {badge && <div style={{ marginBottom: 16 }}><Badge>{badge}</Badge></div>}
    <h2 style={{ fontSize: "clamp(28px,4vw,42px)", fontWeight: 700, color: C.white, margin: 0, lineHeight: 1.2 }}>{title}</h2>
    {subtitle && <p style={{ color: C.muted, fontSize: 17, marginTop: 16, maxWidth: 600, marginLeft: "auto", marginRight: "auto", lineHeight: 1.7 }}>{subtitle}</p>}
  </div>
);

const Input = ({ label, type = "text", placeholder, textarea, value, onChange, rows }) => (
  <div style={{ marginBottom: 20 }}>
    <label style={{ display: "block", color: C.muted, fontSize: 13, fontWeight: 600, marginBottom: 8, letterSpacing: 0.5, textTransform: "uppercase" }}>{label}</label>
    {textarea
      ? <textarea rows={rows || 4} placeholder={placeholder} value={value} onChange={onChange} style={{ width: "100%", padding: "12px 16px", borderRadius: 10, border: `1px solid ${C.border}`, background: "rgba(255,255,255,0.04)", color: C.white, fontSize: 15, fontFamily: "inherit", resize: "vertical", outline: "none", boxSizing: "border-box" }} />
      : <input type={type} placeholder={placeholder} value={value} onChange={onChange} style={{ width: "100%", padding: "12px 16px", borderRadius: 10, border: `1px solid ${C.border}`, background: "rgba(255,255,255,0.04)", color: C.white, fontSize: 15, fontFamily: "inherit", outline: "none", boxSizing: "border-box" }} />
    }
  </div>
);

// ─── BLOG CARD (reusable for home + blog page) ───
const BlogCard = ({ p, showAllTags, onClick }) => (
  <Card style={{ padding: 0, overflow: "hidden" }} onClick={onClick}>
    {p.image && <div style={{ width: "100%", height: 180, overflow: "hidden" }}><img src={p.image} alt={p.title} style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }} /></div>}
    <div style={{ padding: p.image ? "20px 32px 32px" : 32 }}>
      <div style={{ display: "flex", gap: 8, marginBottom: 14, flexWrap: "wrap" }}>{(showAllTags ? p.tags : p.tags.slice(0, 2)).map(t => <Badge key={t}>{t}</Badge>)}</div>
      <h3 style={{ color: C.white, fontSize: 18, fontWeight: 700, margin: "0 0 10px", lineHeight: 1.4 }}>{p.title}</h3>
      <p style={{ color: C.muted, fontSize: 14, lineHeight: 1.7, margin: "0 0 16px" }}>{p.excerpt}</p>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", color: C.muted, fontSize: 13 }}>
        <span>{p.date}</span>
        <span style={{ display: "flex", alignItems: "center", gap: 4 }}><Icons.Clock /> {p.read} read</span>
      </div>
    </div>
  </Card>
);

// ─── BLOG POST VIEW ──────────────────────────────
const BlogPostView = ({ post, onBack }) => (
  <>
    <div style={{ paddingTop: 120, maxWidth: 800, margin: "0 auto", paddingLeft: 24, paddingRight: 24 }}>
      <button onClick={onBack} style={{ display: "inline-flex", alignItems: "center", gap: 8, background: "none", border: "none", color: C.accent, fontSize: 15, fontWeight: 600, cursor: "pointer", fontFamily: "inherit", padding: "8px 0", marginBottom: 32 }}>
        <Icons.ArrowLeft /> Back to Blog
      </button>

      {post.image && (
        <div style={{ width: "100%", borderRadius: 16, overflow: "hidden", marginBottom: 32 }}>
          <img src={post.image} alt={post.title} style={{ width: "100%", height: "auto", display: "block" }} />
        </div>
      )}

      <div style={{ display: "flex", gap: 8, marginBottom: 20, flexWrap: "wrap" }}>
        {post.tags.map(t => <Badge key={t}>{t}</Badge>)}
      </div>

      <h1 style={{ fontSize: "clamp(28px,4vw,44px)", fontWeight: 800, color: C.white, margin: "0 0 16px", lineHeight: 1.2 }}>{post.title}</h1>

      <div style={{ display: "flex", alignItems: "center", gap: 20, color: C.muted, fontSize: 14, marginBottom: 48, paddingBottom: 32, borderBottom: `1px solid ${C.border}` }}>
        <span>{post.date}</span>
        <span style={{ display: "flex", alignItems: "center", gap: 4 }}><Icons.Clock /> {post.read} read</span>
      </div>

      <div style={{ color: C.muted, fontSize: 17, lineHeight: 2 }}>
        {post.content
          ? post.content.split("\n\n").map((para, i) => (
              <p key={i} style={{ marginBottom: 24, color: "#CBD5E1" }}>{para}</p>
            ))
          : <div style={{ textAlign: "center", padding: "60px 0" }}>
              <p style={{ fontSize: 20, color: C.white, fontWeight: 600, marginBottom: 12 }}>Full article coming soon.</p>
              <p style={{ color: C.muted }}>Check back later for the complete post.</p>
            </div>
        }
      </div>

      <div style={{ borderTop: `1px solid ${C.border}`, marginTop: 48, paddingTop: 32, paddingBottom: 60 }}>
        <button onClick={onBack} style={{ display: "inline-flex", alignItems: "center", gap: 8, background: "none", border: "none", color: C.accent, fontSize: 15, fontWeight: 600, cursor: "pointer", fontFamily: "inherit", padding: "8px 0" }}>
          <Icons.ArrowLeft /> Back to Blog
        </button>
      </div>
    </div>
  </>
);

// ─── HOME PAGE ───────────────────────────────────
const HomePage = ({ navigate, openPost }) => (
  <>
    <div style={{ minHeight: "90vh", display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center", position: "relative", overflow: "hidden" }}>
      <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse 80% 60% at 50% 30%, rgba(37,99,235,0.12) 0%, transparent 70%)" }} />
      <div style={{ position: "absolute", top: "15%", left: "10%", width: 300, height: 300, borderRadius: "50%", background: "rgba(37,99,235,0.04)", filter: "blur(80px)" }} />
      <div style={{ position: "absolute", bottom: "20%", right: "10%", width: 250, height: 250, borderRadius: "50%", background: "rgba(37,99,235,0.06)", filter: "blur(60px)" }} />
      <div style={{ position: "relative", zIndex: 1, maxWidth: 800, padding: "0 24px" }}>
        <Badge>{siteSettings.tagline}</Badge>
        <h1 style={{ fontSize: "clamp(36px,6vw,68px)", fontWeight: 800, color: C.white, margin: "24px 0 0", lineHeight: 1.08, letterSpacing: "-0.02em" }}>
          {hero.title}<br /><span style={{ color: C.accent }}>{hero.titleAccent}</span>
        </h1>
        <p style={{ color: C.muted, fontSize: "clamp(16px,2vw,20px)", lineHeight: 1.7, margin: "24px auto 0", maxWidth: 580 }}>{hero.subtitle}</p>
        <div style={{ display: "flex", gap: 16, justifyContent: "center", marginTop: 40, flexWrap: "wrap" }}>
          <Btn onClick={() => navigate("Consulting")}>Consulting Services <Icons.Arrow /></Btn>
          <Btn variant="outline" onClick={() => navigate("Education")}>Learn With Me</Btn>
        </div>
      </div>
    </div>

    <Sec>
      <STitle badge="WHAT I DO" title="Security That Scales With You" subtitle="From startup to enterprise, I help teams build cloud security that actually works — not just checkboxes on an audit." />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: 24 }}>
        {[
          { icon: <Icons.Cloud />, title: "Cloud Security", desc: "Multi-cloud security architecture, IAM design, and compliance for AWS, Azure, and GCP. Real strategies, not checkbox audits.", cl: "#3B82F6" },
          { icon: <Icons.Brain />, title: "AI Security", desc: "Securing ML pipelines, LLM applications, and AI governance frameworks. Protecting your most innovative assets.", cl: "#8B5CF6" },
          { icon: <Icons.Book />, title: "Education & Mentorship", desc: "1-on-1 mentorship, workshops, and curriculum designed to take you from beginner to job-ready in cloud security.", cl: "#10B981" },
        ].map((s, i) => (
          <Card key={i} style={{ textAlign: "center", padding: 40 }}>
            <div style={{ width: 56, height: 56, borderRadius: 14, background: `linear-gradient(135deg, ${s.cl}20, ${s.cl}08)`, display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 20px", color: s.cl }}>{s.icon}</div>
            <h3 style={{ color: C.white, fontSize: 20, fontWeight: 700, margin: "0 0 12px" }}>{s.title}</h3>
            <p style={{ color: C.muted, fontSize: 15, lineHeight: 1.7, margin: 0 }}>{s.desc}</p>
          </Card>
        ))}
      </div>
    </Sec>

    <Sec style={{ paddingTop: 20 }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 24, textAlign: "center" }}>
        {stats.map((s, i) => (
          <div key={i} style={{ padding: 32 }}>
            <div style={{ fontSize: 48, fontWeight: 800, color: C.accent, letterSpacing: "-0.02em" }}>{s.num}</div>
            <div style={{ color: C.muted, fontSize: 15, marginTop: 8, fontWeight: 500 }}>{s.label}</div>
          </div>
        ))}
      </div>
    </Sec>

    <Sec>
      <STitle badge="INSIGHTS" title="From the Blog" subtitle="Practical cloud security knowledge you can apply today." />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: 24 }}>
        {blogPosts.filter(p => p.published).slice(0, 3).map(p => (
          <BlogCard key={p.id} p={p} onClick={() => openPost(p)} />
        ))}
      </div>
      <div style={{ textAlign: "center", marginTop: 40 }}><Btn variant="outline" onClick={() => navigate("Blog")}>View All Posts <Icons.Arrow /></Btn></div>
    </Sec>
  </>
);

// ─── CONSULTING PAGE ─────────────────────────────
const ConsultingPage = ({ navigate }) => (
  <>
    <div style={{ minHeight: "60vh", display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center", position: "relative" }}>
      <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse 70% 50% at 50% 40%, rgba(37,99,235,0.1) 0%, transparent 70%)" }} />
      <div style={{ position: "relative", maxWidth: 700, padding: "0 24px" }}>
        <Badge>CONSULTING</Badge>
        <h1 style={{ fontSize: "clamp(32px,5vw,56px)", fontWeight: 800, color: C.white, margin: "20px 0 0", lineHeight: 1.1 }}>Cloud & AI Security<br /><span style={{ color: C.accent }}>Consulting</span></h1>
        <p style={{ color: C.muted, fontSize: 18, lineHeight: 1.7, marginTop: 20, maxWidth: 550, marginLeft: "auto", marginRight: "auto" }}>Securing your cloud infrastructure and AI systems with pragmatic, risk-focused strategies.</p>
      </div>
    </div>
    <Sec>
      <STitle badge="CLOUD SECURITY" title="Cloud Security Services" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: 24 }}>
        {[
          { icon: <Icons.Cloud />, title: "Multi-Cloud Assessments", pts: ["Comprehensive posture evaluation across AWS, Azure, and GCP", "Misconfiguration detection and remediation roadmap", "Compliance mapping (SOC 2, ISO 27001, NIST, CIS)", "Actionable findings prioritized by business risk"] },
          { icon: <Icons.Lock />, title: "RBAC & IAM Design", pts: ["Least-privilege access architecture", "Cross-cloud identity federation", "Service account governance", "Privileged access management strategy"] },
          { icon: <Icons.Shield />, title: "Architecture Reviews", pts: ["Network segmentation and micro-segmentation", "Encryption at rest and in transit strategy", "Logging, monitoring, and alerting design", "Incident response runbook development"] },
        ].map((s, i) => (
          <Card key={i}>
            <div style={{ color: C.accent, marginBottom: 20 }}>{s.icon}</div>
            <h3 style={{ color: C.white, fontSize: 20, fontWeight: 700, margin: "0 0 16px" }}>{s.title}</h3>
            {s.pts.map((p, j) => <div key={j} style={{ display: "flex", gap: 10, alignItems: "flex-start", marginBottom: 10 }}><div style={{ marginTop: 2 }}><Icons.Check /></div><span style={{ color: C.muted, fontSize: 14, lineHeight: 1.6 }}>{p}</span></div>)}
          </Card>
        ))}
      </div>
    </Sec>
    <Sec style={{ paddingTop: 20 }}>
      <STitle badge="AI SECURITY" title="AI & ML Security Services" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(380px, 1fr))", gap: 24 }}>
        {[
          { title: "AI/ML Pipeline Security", desc: "End-to-end security for your machine learning lifecycle — from data ingestion and model training to deployment and inference. Covering data poisoning prevention, model integrity, and secure serving." },
          { title: "AI Governance & Compliance", desc: "Building governance frameworks that keep your AI systems trustworthy and compliant. Risk assessment, bias auditing, model inventory management, and regulatory alignment." },
        ].map((s, i) => (
          <Card key={i} style={{ padding: 40 }}>
            <div style={{ width: 48, height: 48, borderRadius: 12, background: "linear-gradient(135deg, rgba(139,92,246,0.2), rgba(139,92,246,0.05))", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 20, color: "#8B5CF6" }}><Icons.Brain /></div>
            <h3 style={{ color: C.white, fontSize: 22, fontWeight: 700, margin: "0 0 14px" }}>{s.title}</h3>
            <p style={{ color: C.muted, fontSize: 15, lineHeight: 1.8, margin: 0 }}>{s.desc}</p>
          </Card>
        ))}
      </div>
    </Sec>
    <Sec style={{ paddingTop: 20 }}>
      <STitle badge="APPROACH" title="How I Work" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 24 }}>
        {[{ s: "01", t: "Discover", d: "Deep dive into your environment, architecture, and business context." }, { s: "02", t: "Assess", d: "Identify risks, misconfigurations, and gaps mapped to industry frameworks." }, { s: "03", t: "Prioritize", d: "Rank findings by actual business impact — not theoretical severity." }, { s: "04", t: "Remediate", d: "Hands-on guidance and implementation support to close gaps fast." }].map((s, i) => (
          <Card key={i} style={{ textAlign: "center", padding: 36 }}>
            <div style={{ fontSize: 36, fontWeight: 800, color: C.accent, opacity: 0.6, marginBottom: 12 }}>{s.s}</div>
            <h4 style={{ color: C.white, fontSize: 18, fontWeight: 700, margin: "0 0 10px" }}>{s.t}</h4>
            <p style={{ color: C.muted, fontSize: 14, lineHeight: 1.7, margin: 0 }}>{s.d}</p>
          </Card>
        ))}
      </div>
    </Sec>
    <Sec style={{ paddingTop: 20 }}>
      <STitle badge="RESULTS" title="Case Studies" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: 24 }}>
        {caseStudies.map((s, i) => (
          <Card key={i}>
            <h3 style={{ color: C.white, fontSize: 18, fontWeight: 700, margin: "0 0 8px" }}>{s.title}</h3>
            <div style={{ color: C.green, fontSize: 14, fontWeight: 700, marginBottom: 14, display: "flex", alignItems: "center", gap: 6 }}><Icons.Check /> {s.result}</div>
            <p style={{ color: C.muted, fontSize: 14, lineHeight: 1.7, margin: 0 }}>{s.desc}</p>
          </Card>
        ))}
      </div>
    </Sec>
    <Sec style={{ paddingTop: 20 }}>
      <Card hover={false} style={{ textAlign: "center", padding: "60px 40px", background: "linear-gradient(135deg, rgba(37,99,235,0.12), rgba(37,99,235,0.03))", border: "1px solid rgba(37,99,235,0.2)" }}>
        <h2 style={{ color: C.white, fontSize: 32, fontWeight: 800, margin: "0 0 16px" }}>Ready to Secure Your Cloud?</h2>
        <p style={{ color: C.muted, fontSize: 17, maxWidth: 500, margin: "0 auto 32px" }}>Let's discuss your security challenges and build a strategy that fits.</p>
        <Btn onClick={() => setEnrollCourse(course)}>Get In Touch <Icons.Arrow /></Btn>
      </Card>
    </Sec>
  </>
);

// ─── EDUCATION PAGE ──────────────────────────────
const [enrollCourse, setEnrollCourse] = useState(null);
const courses = [
    {
      id: "c1",
      badge: "FUNDAMENTALS",
      badgeColor: "#10B981",
      label: null,
      title: "Cloud Security Fundamentals",
      desc:
        "A fast-track, live training program for professionals who want to build a real foundation in cloud security,  not just pass an exam.  With hands-on, real-world experience across AWS & Azure, .",
      duration: "4 weeks · 2x per week",
      includes: ["Live training sessions", "Course resources & materials"],
      outcomes: [],
      price: "$499",
      commitment: null,
      cta: "Enroll Now",
    },
    {
      id: "c2",
      badge: "MOST COMPREHENSIVE",
      badgeColor: "#2563EB",
      label: "Most Comprehensive",
      title: "Azure Cloud Security",
      desc:
        "A deep dive 12-week live program covering Azure security architecture, identity, compliance, and threat protection — built for professionals who want to stand out in the job market with real-world skills.",
      duration: "12 weeks",
      includes: [
        "Live training sessions",
        "Resume review",
        "Interview prep",
        "Hands-on Labs",
        "Course resources & materials",
        "Final Capstone project(real-world security implementation focused"
      ],
      outcomes: [],
      price: "$2,300",
      commitment: null,
      cta: "Enroll Now",
    },
    {
      id: "c3",
      badge: "1-ON-1 MENTORSHIP",
      badgeColor: "#10B981",
      label: null,
      title: "Mentorship — 1-on-1",
      desc:
        "Personalized weekly sessions with a mentor who tailors every session to your goals, your gaps, and your career trajectory. This isn't a course,  it's a direct line to someone who's done it.",
      duration: "Weekly sessions",
      includes: [
        "Deep dive 1-on-1 sessions",
        "Resume review",
        "Interview prep",
        "Resources & materials",
        "Capstone project tailored to your chosen niche(real-world security implementation focused)",
      ],
      outcomes: [],
      price: "$599 / mo",
      commitment: "3-month minimum commitment",
      cta: "Apply Now",
    },
    {
      id: "c4",
      badge: "GROUP MENTORSHIP",
      badgeColor: "#10B981",
      label: null,
      title: "Mentorship — Group",
      desc:
        "All the benefits of the mentorship program in a collaborative group setting. Learn alongside peers, share real-world challenges, and get expert guidance .",
      duration: "Weekly sessions",
      includes: [
        "Group deep dive sessions",
        "Resume review",
        "Resources & materials",
      ],
      outcomes: [],
      price: "$299 / mo",
      commitment: "3-month minimum commitment",
      cta: "Apply Now",
    },
  ];
  return (
    <>
      {/* ── Hero ── */}
      <div
        style={{
          minHeight: "60vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          textAlign: "center",
          position: "relative",
        }}
      >
        <div
          style={{
            position: "absolute",
            inset: 0,
            background:
              "radial-gradient(ellipse 70% 50% at 50% 40%, rgba(16,185,129,0.08) 0%, transparent 70%)",
          }}
        />
        <div
          style={{ position: "relative", maxWidth: 700, padding: "0 24px" }}
        >
          <Badge>EDUCATION</Badge>
          <h1
            style={{
              fontSize: "clamp(32px,5vw,56px)",
              fontWeight: 800,
              color: C.white,
              margin: "20px 0 0",
              lineHeight: 1.1,
            }}
          >
            Level Up Your Cloud
            <br />
            <span style={{ color: "#10B981" }}>&amp; AI Security Skills</span>
          </h1>
          <p
            style={{
              color: C.muted,
              fontSize: 18,
              lineHeight: 1.7,
              marginTop: 20,
            }}
          >
            Hands-on training designed to take you from where you are to where
            you want to be with real-world experience.
          </p>
        </div>
      </div>

      {/* ── Course Cards ── */}
      <Sec>
        <STitle badge="PROGRAMS" title="Choose Your Path" />
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(290px, 1fr))",
            gap: 24,
          }}
        >
          {courses.map((course) => (
            <Card
              key={course.id}
              style={{
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                padding: 28,
                position: "relative",
                ...(course.label === "Most Comprehensive"
                  ? {
                      border: "1px solid rgba(37,99,235,0.5)",
                      background:
                        "linear-gradient(135deg, rgba(37,99,235,0.08), rgba(37,99,235,0.02))",
                    }
                  : {}),
              }}
            >
              {/* Top label ribbon */}
              {course.label && (
                <div
                  style={{
                    position: "absolute",
                    top: -1,
                    right: 20,
                    background: "#2563EB",
                    color: "#fff",
                    fontSize: 11,
                    fontWeight: 700,
                    padding: "4px 12px",
                    borderRadius: "0 0 8px 8px",
                    letterSpacing: "0.05em",
                    textTransform: "uppercase",
                  }}
                >
                  {course.label}
                </div>
              )}

              <div>
                {/* Badge + title */}
                <div style={{ marginBottom: 12 }}>
                  <span
                    style={{
                      fontSize: 11,
                      fontWeight: 700,
                      letterSpacing: "0.08em",
                      textTransform: "uppercase",
                      color: course.badgeColor,
                      opacity: 0.9,
                    }}
                  >
                    {course.badge}
                  </span>
                </div>
                <h3
                  style={{
                    color: C.white,
                    fontSize: 20,
                    fontWeight: 700,
                    margin: "0 0 10px",
                  }}
                >
                  {course.title}
                </h3>
                <p
                  style={{
                    color: C.muted,
                    fontSize: 14,
                    lineHeight: 1.7,
                    margin: "0 0 18px",
                  }}
                >
                  {course.desc}
                </p>

                {/* Duration */}
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    marginBottom: 14,
                  }}
                >
                  <span style={{ color: course.badgeColor, fontSize: 14 }}>
                    ⏱
                  </span>
                  <span
                    style={{
                      color: C.muted,
                      fontSize: 13,
                      fontWeight: 600,
                    }}
                  >
                    {course.duration}
                  </span>
                </div>

                {/* Includes */}
                <div style={{ marginBottom: 16 }}>
                  <div
                    style={{
                      color: C.white,
                      fontSize: 12,
                      fontWeight: 700,
                      textTransform: "uppercase",
                      letterSpacing: "0.06em",
                      marginBottom: 8,
                      opacity: 0.6,
                    }}
                  >
                    Includes
                  </div>
                  {course.includes.map((item, i) => (
                    <div
                      key={i}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 8,
                        marginBottom: 6,
                      }}
                    >
                      <span style={{ color: course.badgeColor, fontSize: 13 }}>
                        ✓
                      </span>
                      <span style={{ color: C.muted, fontSize: 13 }}>
                        {item}
                      </span>
                    </div>
                  ))}
                </div>

                {/* Commitment note */}
                {course.commitment && (
                  <div
                    style={{
                      background: "rgba(255,255,255,0.04)",
                      border: "1px solid rgba(255,255,255,0.08)",
                      borderRadius: 8,
                      padding: "8px 12px",
                      marginBottom: 16,
                      fontSize: 12,
                      color: C.muted,
                      fontStyle: "italic",
                    }}
                  >
                    📅 {course.commitment}
                  </div>
                )}
              </div>

              {/* Price + CTA */}
              <div style={{ marginTop: 8 }}>
                <div
                  style={{
                    color: C.white,
                    fontSize: 22,
                    fontWeight: 800,
                    marginBottom: 14,
                  }}
                >
                  {course.price}
                </div>
                <Btn
                  onClick={() => setEnrollCourse(course)}
                  style={
                    course.label === "Most Comprehensive"
                      ? {}
                      : {
                          background: "rgba(16,185,129,0.15)",
                          border: "1px solid rgba(16,185,129,0.4)",
                          color: "#10B981",
                        }
                  }
                >
                  {course.cta} <Icons.Arrow />
                </Btn>
              </div>
            </Card>
          ))}
        </div>
      </Sec>

      {/* ── Testimonials (only if populated) ── */}
      {(ct.testimonials || []).length > 0 && (
        <Sec style={{ paddingTop: 20 }}>
          <STitle badge="TESTIMONIALS" title="What Students Say" />
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
              gap: 24,
            }}
          >
          {(ct.testimonials || []).map((t, i) => (
              <Card key={i}>
                <div
                  style={{ display: "flex", gap: 2, marginBottom: 14 }}
                >
                  {[1, 2, 3, 4, 5].map((j) => (
                    <Icons.Star key={j} />
                  ))}
                </div>
                <p
                  style={{
                    color: C.muted,
                    fontSize: 14,
                    lineHeight: 1.8,
                    margin: "0 0 16px",
                    fontStyle: "italic",
                  }}
                >
                  "{t.text}"
                </p>
                <div>
                  <div
                    style={{
                      color: C.white,
                      fontSize: 15,
                      fontWeight: 700,
                    }}
                  >
                    {t.name}
                  </div>
                  <div
                    style={{
                      color: C.muted,
                      fontSize: 13,
                      marginTop: 2,
                    }}
                  >
                    {t.role}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </Sec>
      )}

      {/* ── CTA ── */}
      <Sec style={{ paddingTop: 20 }}>
        <Card
          hover={false}
          style={{
            textAlign: "center",
            padding: "60px 40px",
            background:
              "linear-gradient(135deg, rgba(16,185,129,0.12), rgba(16,185,129,0.03))",
            border: "1px solid rgba(16,185,129,0.2)",
          }}
        >
          <h2
            style={{
              color: C.white,
              fontSize: 32,
              fontWeight: 800,
              margin: "0 0 16px",
            }}
          >
            Ready to Start Learning?
          </h2>
          <p
            style={{
              color: C.muted,
              fontSize: 17,
              maxWidth: 500,
              margin: "0 auto 32px",
            }}
          >
            Whether you're just starting out or ready to level up, there's a
            path for you.
          </p>
          <Btn onClick={() => setEnrollCourse(course)}>
            Get In Touch <Icons.Arrow />
          </Btn>
        </Card>
      </Sec>
   {enrollCourse && <EnrollmentForm course={enrollCourse} onClose={() => setEnrollCourse(null)} />}
    </>
  );
};

// ─── END OF EDUCATION PAGE ────────────────────────────────────────────────────
// ─── BLOG PAGE ───────────────────────────────────
const BlogPage = ({ openPost }) => {
  const [search, setSearch] = useState("");
  const [activeTag, setActiveTag] = useState(null);
  const [page, setPage] = useState(1);
  const perPage = 4;
  const published = blogPosts.filter(p => p.published);
  const filtered = published.filter(p => {
    const ms = !search || p.title.toLowerCase().includes(search.toLowerCase()) || p.excerpt.toLowerCase().includes(search.toLowerCase());
    const mt = !activeTag || p.tags.includes(activeTag);
    return ms && mt;
  });
  const totalPages = Math.ceil(filtered.length / perPage);
  const paged = filtered.slice((page - 1) * perPage, page * perPage);

  return (
    <>
      <div style={{ minHeight: "40vh", display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center", paddingTop: 80 }}>
        <div style={{ maxWidth: 600, padding: "0 24px" }}>
          <Badge>BLOG</Badge>
          <h1 style={{ fontSize: "clamp(32px,5vw,48px)", fontWeight: 800, color: C.white, margin: "20px 0 0" }}>Insights & Guides</h1>
          <p style={{ color: C.muted, fontSize: 17, marginTop: 16 }}>Practical cloud and AI security knowledge from the field.</p>
        </div>
      </div>
      <Sec style={{ paddingTop: 40 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, background: C.bgCard, border: `1px solid ${C.border}`, borderRadius: 12, padding: "12px 20px", marginBottom: 24, maxWidth: 500 }}>
          <Icons.Search />
          <input value={search} onChange={e => { setSearch(e.target.value); setPage(1); }} placeholder="Search articles..." style={{ flex: 1, background: "transparent", border: "none", outline: "none", color: C.white, fontSize: 15, fontFamily: "inherit" }} />
        </div>
        <div style={{ display: "flex", gap: 8, marginBottom: 40, flexWrap: "wrap" }}>
          <button onClick={() => { setActiveTag(null); setPage(1); }} style={{ padding: "6px 16px", borderRadius: 20, fontSize: 13, fontWeight: 600, cursor: "pointer", border: `1px solid ${!activeTag ? C.accent : C.border}`, background: !activeTag ? C.accent : "transparent", color: !activeTag ? "#fff" : C.muted, fontFamily: "inherit" }}>All</button>
          {ALL_TAGS.map(t => <button key={t} onClick={() => { setActiveTag(activeTag === t ? null : t); setPage(1); }} style={{ padding: "6px 16px", borderRadius: 20, fontSize: 13, fontWeight: 600, cursor: "pointer", border: `1px solid ${activeTag === t ? C.accent : C.border}`, background: activeTag === t ? C.accent : "transparent", color: activeTag === t ? "#fff" : C.muted, fontFamily: "inherit" }}>{t}</button>)}
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: 24 }}>
          {paged.map(p => (
            <BlogCard key={p.id} p={p} showAllTags onClick={() => openPost(p)} />
          ))}
        </div>
        {paged.length === 0 && <div style={{ textAlign: "center", padding: 60, color: C.muted }}><p style={{ fontSize: 18 }}>No articles match your search.</p></div>}
        {totalPages > 1 && <div style={{ display: "flex", justifyContent: "center", gap: 8, marginTop: 40 }}>{Array.from({ length: totalPages }, (_, i) => i + 1).map(n => <button key={n} onClick={() => setPage(n)} style={{ width: 40, height: 40, borderRadius: 10, fontSize: 14, fontWeight: 600, cursor: "pointer", border: n === page ? "none" : `1px solid ${C.border}`, fontFamily: "inherit", background: n === page ? C.accent : "transparent", color: n === page ? "#fff" : C.muted }}>{n}</button>)}</div>}
      </Sec>
    </>
  );
};

// ─── ABOUT PAGE ──────────────────────────────────
const AboutPage = () => (
  <>
    <div style={{ minHeight: "40vh", display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center", paddingTop: 80 }}>
      <div style={{ maxWidth: 600, padding: "0 24px" }}><Badge>ABOUT</Badge><h1 style={{ fontSize: "clamp(32px,5vw,48px)", fontWeight: 800, color: C.white, margin: "20px 0 0" }}>The Person Behind SubtleTech</h1></div>
    </div>
    <Sec style={{ paddingTop: 20 }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", gap: 48, alignItems: "start" }}>
        <div style={{ width: "100%", aspectRatio: "1", maxWidth: 400, borderRadius: 24, background: `linear-gradient(135deg, ${C.bgCard}, rgba(37,99,235,0.1))`, border: `1px solid ${C.border}`, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <div style={{ textAlign: "center", color: C.muted }}><div style={{ fontSize: 64, marginBottom: 12 }}>🛡️</div><div style={{ fontSize: 15, fontWeight: 600 }}>Your Cloud Security Guy</div></div>
        </div>
        <div>
          <h2 style={{ color: C.white, fontSize: 28, fontWeight: 800, margin: "0 0 20px" }}>{about.headline}</h2>
          <div style={{ color: C.muted, fontSize: 15, lineHeight: 1.9 }}>
            {about.bio.split("\n\n").map((p, i) => <p key={i} style={{ marginTop: i ? 16 : 0 }}>{p}</p>)}
          </div>
        </div>
      </div>
    </Sec>
    <Sec style={{ paddingTop: 20 }}>
      <STitle badge="EXPERTISE" title="What I Specialize In" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 20 }}>
        {about.expertise.map((e, i) => <Card key={i} style={{ padding: 20, textAlign: "center" }}><span style={{ color: C.white, fontSize: 14, fontWeight: 600 }}>{e}</span></Card>)}
      </div>
    </Sec>
    <Sec style={{ paddingTop: 20 }}>
      <STitle badge="CERTIFICATIONS" title="Credentials That Back It Up" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 20 }}>
        {about.certifications.map((c, i) => <Card key={i} style={{ padding: 20, display: "flex", alignItems: "center", gap: 14 }}><div style={{ color: C.accent, flexShrink: 0 }}><Icons.Cert /></div><span style={{ color: C.white, fontSize: 14, fontWeight: 600 }}>{c}</span></Card>)}
      </div>
    </Sec>
  </>
);

// ─── CONNECT PAGE ────────────────────────────────
const ConnectPage = () => {
  const [form, setForm] = useState({ name: "", email: "", message: "" });
  const [sent, setSent] = useState(false);

  return (
    <>
      <div style={{ minHeight: "40vh", display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center", paddingTop: 80 }}>
        <div style={{ maxWidth: 600, padding: "0 24px" }}>
          <Badge>CONNECT</Badge>
          <h1 style={{ fontSize: "clamp(32px,5vw,48px)", fontWeight: 800, color: C.white, margin: "20px 0 0" }}>Let's Work Together</h1>
          <p style={{ color: C.muted, fontSize: 17, marginTop: 16 }}>Looking for consulting, mentorship, or just want to connect — I'd love to hear from you.</p>
        </div>
      </div>
      <Sec style={{ paddingTop: 40 }}>
        <STitle title="Find Me Everywhere" />
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: 20 }}>
          {socials.map((s, i) => (
            <Card key={i}>
              <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 14 }}>
                <div style={{ width: 44, height: 44, borderRadius: 12, background: `${s.color}18`, display: "flex", alignItems: "center", justifyContent: "center", color: s.color }}><SocialIcon type={s.type} /></div>
                <h3 style={{ color: C.white, fontSize: 18, fontWeight: 700, margin: 0 }}>{s.name}</h3>
              </div>
              <p style={{ color: C.muted, fontSize: 14, lineHeight: 1.7, margin: "0 0 16px" }}>{s.desc}</p>
              <a href={s.url} target="_blank" rel="noopener noreferrer" style={{ color: C.accent, fontSize: 14, fontWeight: 600, cursor: "pointer", display: "inline-flex", alignItems: "center", gap: 6, textDecoration: "none" }}>{s.cta} <Icons.Ext /></a>
            </Card>
          ))}
        </div>
      </Sec>
      <Sec style={{ paddingTop: 20 }}>
        <STitle badge="INQUIRY" title="Send a Message" subtitle="For consulting, mentorship, or anything else." />
        <Card hover={false} style={{ maxWidth: 600, margin: "0 auto", padding: 40 }}>
          {sent ? (
            <div style={{ textAlign: "center", padding: 40 }}>
              <div style={{ fontSize: 48, marginBottom: 16 }}>✉️</div>
              <h3 style={{ color: C.white, fontSize: 22, fontWeight: 700, margin: "0 0 12px" }}>Message Sent!</h3>
              <p style={{ color: C.muted, fontSize: 15 }}>I'll get back to you within 24-48 hours at <strong style={{ color: C.white }}>{siteSettings.email}</strong></p>
              <Btn style={{ marginTop: 24 }} onClick={() => { setSent(false); setForm({ name: "", email: "", message: "" }); }}>Send Another</Btn>
            </div>
          ) : (
            <>
              <Input label="Name" placeholder="Your name" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} />
              <Input label="Email" type="email" placeholder="you@email.com" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
              <Input label="Message" textarea placeholder="Tell me about your project, goals, or questions..." value={form.message} onChange={e => setForm({ ...form, message: e.target.value })} />
              <Btn style={{ width: "100%", justifyContent: "center" }} onClick={() => { if (form.name && form.email && form.message) setSent(true); }}>Send Message <Icons.Arrow /></Btn>
            </>
          )}
        </Card>
      </Sec>
    </>
  );
};

// ─── MAIN APP ────────────────────────────────────
export default function App() {
  const [page, setPage] = useState("Home");
  const [mob, setMob] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [activePost, setActivePost] = useState(null);

  useEffect(() => {
    const h = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", h);
    return () => window.removeEventListener("scroll", h);
  }, []);

  const navigate = (p) => { setPage(p); setMob(false); setActivePost(null); window.scrollTo({ top: 0, behavior: "smooth" }); };
  const openPost = (post) => { setActivePost(post); setPage("Blog"); window.scrollTo({ top: 0, behavior: "smooth" }); };
  const closePost = () => { setActivePost(null); window.scrollTo({ top: 0, behavior: "smooth" }); };

  return (
    <div style={{ background: C.bg, minHeight: "100vh", color: C.white }}>
      {/* NAV */}
      <nav style={{ position: "fixed", top: 0, left: 0, right: 0, zIndex: 100, padding: "0 24px", background: scrolled ? C.bgNav : "transparent", backdropFilter: scrolled ? "blur(20px)" : "none", borderBottom: scrolled ? `1px solid ${C.border}` : "1px solid transparent", transition: "all 0.3s" }}>
        <div style={{ maxWidth: 1200, margin: "0 auto", display: "flex", alignItems: "center", justifyContent: "space-between", height: 72 }}>
          <div onClick={() => navigate("Home")} style={{ cursor: "pointer", display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{ width: 36, height: 36, borderRadius: 10, background: `linear-gradient(135deg, ${C.accent}, #1D4ED8)`, display: "flex", alignItems: "center", justifyContent: "center" }}><Icons.Shield /></div>
            <span style={{ fontSize: 20, fontWeight: 800, letterSpacing: "-0.02em" }}>{siteSettings.siteName.replace("Tech", "")}<span style={{ color: C.accent }}>Tech</span></span>
          </div>

          {/* Desktop */}
          <div className="desktop-nav" style={{ display: "flex", alignItems: "center", gap: 8 }}>
            {PAGES.map(p => <button key={p} onClick={() => navigate(p)} style={{ padding: "8px 16px", borderRadius: 8, fontSize: 14, fontWeight: 500, cursor: "pointer", background: page === p ? C.glow : "transparent", color: page === p ? C.white : C.muted, border: "none", fontFamily: "inherit", transition: "all 0.2s" }}>{p}</button>)}
            <Btn style={{ marginLeft: 8, padding: "10px 22px", fontSize: 14 }} onClick={() => navigate("Connect")}>Get Started</Btn>
          </div>

          {/* Mobile */}
          <button onClick={() => setMob(!mob)} className="mobile-toggle" style={{ display: "none", background: "none", border: "none", color: C.white, cursor: "pointer", padding: 8 }}>{mob ? <Icons.X /> : <Icons.Menu />}</button>
        </div>

        {mob && (
          <div style={{ position: "absolute", top: 72, left: 0, right: 0, background: C.bgNav, backdropFilter: "blur(20px)", borderBottom: `1px solid ${C.border}`, padding: "16px 24px", animation: "fadeIn 0.2s" }}>
            {PAGES.map(p => <button key={p} onClick={() => navigate(p)} style={{ display: "block", width: "100%", textAlign: "left", padding: "12px 16px", borderRadius: 8, fontSize: 15, fontWeight: 500, cursor: "pointer", border: "none", fontFamily: "inherit", background: page === p ? C.glow : "transparent", color: page === p ? C.white : C.muted }}>{p}</button>)}
            <div style={{ padding: "12px 0 0" }}><Btn style={{ width: "100%", justifyContent: "center" }} onClick={() => navigate("Connect")}>Get Started</Btn></div>
          </div>
        )}
      </nav>

      <style>{`
        @media (max-width: 768px) { .desktop-nav { display: none !important; } .mobile-toggle { display: block !important; } }
        @media (min-width: 769px) { .mobile-toggle { display: none !important; } }
      `}</style>

      {/* PAGES */}
      <div key={activePost ? activePost.id : page} style={{ animation: "fadeIn 0.4s ease" }}>
        {activePost ? <BlogPostView post={activePost} onBack={closePost} /> :
          <>
            {page === "Home" && <HomePage navigate={navigate} openPost={openPost} />}
            {page === "Consulting" && <ConsultingPage navigate={navigate} />}
            {page === "Education" && <EducationPage content={{ testimonials }} navigate={navigate} />}
            {page === "Blog" && <BlogPage openPost={openPost} />}
            {page === "About" && <AboutPage />}
            {page === "Connect" && <ConnectPage />}
          </>
        }
      </div>

      {/* FOOTER */}
      <footer style={{ borderTop: `1px solid ${C.border}`, background: C.bgCard, marginTop: 40 }}>
        <div style={{ maxWidth: 1200, margin: "0 auto", padding: "60px 24px 40px" }}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 40, marginBottom: 40 }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
                <div style={{ width: 32, height: 32, borderRadius: 8, background: `linear-gradient(135deg, ${C.accent}, #1D4ED8)`, display: "flex", alignItems: "center", justifyContent: "center" }}><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" /></svg></div>
                <span style={{ fontSize: 18, fontWeight: 800 }}>Subtle<span style={{ color: C.accent }}>Tech</span></span>
              </div>
              <p style={{ color: C.muted, fontSize: 14, lineHeight: 1.7 }}>Cloud security consulting and education. Making security practical and empowering.</p>
              <p style={{ color: C.muted, fontSize: 13, marginTop: 12 }}>{siteSettings.email}</p>
            </div>
            <div>
              <h4 style={{ color: C.white, fontSize: 14, fontWeight: 700, marginBottom: 16, textTransform: "uppercase", letterSpacing: 0.5 }}>Services</h4>
              {["Cloud Security Consulting", "AI Security Consulting", "1-on-1 Mentorship", "Workshops & Training"].map(l => <div key={l} style={{ color: C.muted, fontSize: 14, marginBottom: 10, cursor: "pointer" }}>{l}</div>)}
            </div>
            <div>
              <h4 style={{ color: C.white, fontSize: 14, fontWeight: 700, marginBottom: 16, textTransform: "uppercase", letterSpacing: 0.5 }}>Resources</h4>
              {["Blog", "Free Labs", "YouTube Channel", "Discord Community"].map(l => <div key={l} style={{ color: C.muted, fontSize: 14, marginBottom: 10, cursor: "pointer" }}>{l}</div>)}
            </div>
            <div>
              <h4 style={{ color: C.white, fontSize: 14, fontWeight: 700, marginBottom: 16, textTransform: "uppercase", letterSpacing: 0.5 }}>Follow</h4>
              <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                {["youtube", "twitter", "linkedin", "instagram", "tiktok", "discord"].map(s => <div key={s} style={{ width: 40, height: 40, borderRadius: 10, background: "rgba(255,255,255,0.04)", border: `1px solid ${C.border}`, display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", color: C.muted }}><SocialIcon type={s} /></div>)}
              </div>
            </div>
          </div>
          <div style={{ borderTop: `1px solid ${C.border}`, paddingTop: 24, display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 16 }}>
            <span style={{ color: C.muted, fontSize: 13 }}>{siteSettings.copyright}</span>
            <div style={{ display: "flex", gap: 24 }}>{["Privacy Policy", "Terms of Service"].map(l => <span key={l} style={{ color: C.muted, fontSize: 13, cursor: "pointer" }}>{l}</span>)}</div>
          </div>
        </div>
      </footer>
    </div>
  );
}
// ─── ENROLLMENT FORM WITH EMAILJS ────────────────
// Paste this into App.jsx alongside your other components
// Replace YOUR_SERVICE_ID, YOUR_TEMPLATE_ID, YOUR_PUBLIC_KEY
// with your real values from emailjs.com

const EnrollmentForm = ({ course, onClose }) => {
  const isMentorship = course.id === "c3" || course.id === "c4";
  const [form, setForm] = useState({
    name: "", email: "", linkedin: "",
    experience: "", goal: "", start: "", question: "",
  });
  const [submitted, setSubmitted] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });
  const valid = form.name && form.email && form.experience && form.goal;

  const handleSubmit = async () => {
    if (!valid) return;
    setSending(true);
    setError("");

    const templateParams = {
      course_name: course.title,
      course_price: `$${course.price.toLocaleString()} · ${course.priceNote}`,
      type: isMentorship ? "Mentorship Application" : "Course Enrollment",
      name: form.name,
      email: form.email,
      linkedin: form.linkedin || "Not provided",
      experience: form.experience,
      goal: form.goal,
      start: form.start || "Not specified",
      question: form.question || "None",
      to_email: "subtletechie@outlook.com",
    };

    try {
      await window. emailjs.send(
        "service_fgwi0qv",    // 👈 replace with your EmailJS Service ID
       "template_xcsa9ib",   // 👈 replace with your EmailJS Template ID
        templateParams,
        "swg7Xlz_WGzyoBXL"    // 👈 replace with your EmailJS Public Key
      );
      setSubmitted(true);
    } catch (err) {
      setError("Something went wrong. Please email subtletechie@outlook.com directly.");
    } finally {
      setSending(false);
    }
  };

  const fieldStyle = {
    width: "100%", padding: "10px 14px", borderRadius: 10,
    border: `1px solid rgba(148,163,184,0.12)`,
    background: "rgba(255,255,255,0.04)", color: "#F1F5F9",
    fontSize: 14, fontFamily: "inherit", outline: "none", boxSizing: "border-box",
  };

  const labelStyle = {
    display: "block", color: "#94A3B8", fontSize: 11,
    fontWeight: 700, marginBottom: 6,
    textTransform: "uppercase", letterSpacing: 0.5,
  };

  return (
    <div
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
      style={{
        position: "fixed", inset: 0, zIndex: 200,
        background: "rgba(0,0,0,0.75)", backdropFilter: "blur(8px)",
        display: "flex", alignItems: "center", justifyContent: "center",
        padding: 24,
      }}
    >
      <div style={{
        background: "#111B2E", border: `1px solid rgba(37,99,235,0.25)`,
        borderRadius: 20, padding: 40, width: "100%", maxWidth: 560,
        position: "relative", boxShadow: "0 24px 80px rgba(0,0,0,0.5)",
        maxHeight: "90vh", overflowY: "auto",
      }}>
        {/* Close button */}
        <button onClick={onClose} style={{
          position: "absolute", top: 20, right: 20,
          background: "rgba(255,255,255,0.06)", border: "none",
          borderRadius: 8, width: 32, height: 32, cursor: "pointer",
          color: "#94A3B8", fontSize: 18, display: "flex",
          alignItems: "center", justifyContent: "center",
        }}>✕</button>

        {submitted ? (
          // ── Success state ──
          <div style={{ textAlign: "center", padding: "20px 0" }}>
            <div style={{ fontSize: 56, marginBottom: 16 }}>🎉</div>
            <h3 style={{ color: "#F1F5F9", fontSize: 24, fontWeight: 800, margin: "0 0 12px" }}>
              {isMentorship ? "Application Received!" : "Enrollment Request Received!"}
            </h3>
            <p style={{ color: "#94A3B8", fontSize: 15, lineHeight: 1.7, maxWidth: 380, margin: "0 auto 24px" }}>
              {isMentorship
                ? "Thanks for applying! I'll review your application and reach out within 24–48 hours to set up a quick intro call."
                : "Thanks! I'll confirm your spot and send next steps to your email within 24–48 hours."}
            </p>
            <div style={{ background: "rgba(37,99,235,0.08)", border: "1px solid rgba(37,99,235,0.2)", borderRadius: 12, padding: 16, marginBottom: 28 }}>
              <p style={{ color: "#94A3B8", fontSize: 13, margin: 0 }}>
                📧 Confirmation coming to <strong style={{ color: "#F1F5F9" }}>{form.email}</strong>
              </p>
            </div>
            <Btn onClick={onClose}>Back to Courses</Btn>
          </div>
        ) : (
          <>
            {/* ── Header ── */}
            <div style={{ marginBottom: 28 }}>
              <span style={{
                display: "inline-block", padding: "4px 12px", borderRadius: 20,
                fontSize: 11, fontWeight: 700, letterSpacing: 0.5,
                textTransform: "uppercase", background: "rgba(37,99,235,0.15)",
                color: "#3B82F6", marginBottom: 12,
              }}>
                {isMentorship ? "Mentorship Application" : "Course Enrollment"}
              </span>
              <h2 style={{ color: "#F1F5F9", fontSize: 22, fontWeight: 800, margin: "0 0 6px" }}>
                {course.title}
              </h2>
              <p style={{ color: "#94A3B8", fontSize: 14, margin: 0 }}>
                ${course.price.toLocaleString()} · {course.sessions}
              </p>
            </div>

            {/* ── Name + Email row ── */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0 16px" }}>
              <div style={{ marginBottom: 16 }}>
                <label style={labelStyle}>Full Name <span style={{ color: "#F87171" }}>*</span></label>
                <input value={form.name} onChange={set("name")} placeholder="Jane Smith" style={fieldStyle} />
              </div>
              <div style={{ marginBottom: 16 }}>
                <label style={labelStyle}>Email <span style={{ color: "#F87171" }}>*</span></label>
                <input type="email" value={form.email} onChange={set("email")} placeholder="you@email.com" style={fieldStyle} />
              </div>
            </div>

            {/* ── LinkedIn (mentorship only) ── */}
            {isMentorship && (
              <div style={{ marginBottom: 16 }}>
                <label style={labelStyle}>LinkedIn Profile URL</label>
                <input value={form.linkedin} onChange={set("linkedin")} placeholder="linkedin.com/in/yourname" style={fieldStyle} />
              </div>
            )}

            {/* ── Experience ── */}
            <div style={{ marginBottom: 16 }}>
              <label style={labelStyle}>Current Experience Level <span style={{ color: "#F87171" }}>*</span></label>
              <select value={form.experience} onChange={set("experience")}
                style={{ ...fieldStyle, background: "#111B2E", color: form.experience ? "#F1F5F9" : "#94A3B8" }}>
                <option value="" disabled>Select your level...</option>
                <option value="No cybersecurity experience yet">No cybersecurity experience yet</option>
                <option value="Beginner (0–1 years)">Beginner (0–1 years)</option>
                <option value="Intermediate (1–3 years)">Intermediate (1–3 years)</option>
                <option value="Advanced (3+ years)">Advanced (3+ years)</option>
              </select>
            </div>

            {/* ── Goal ── */}
            <div style={{ marginBottom: 16 }}>
              <label style={labelStyle}>What's your main goal? <span style={{ color: "#F87171" }}>*</span></label>
              <textarea rows={3} value={form.goal} onChange={set("goal")}
                placeholder={isMentorship ? "e.g. Break into cloud security, get promoted..." : "e.g. Understand Azure security for my current role..."}
                style={{ ...fieldStyle, resize: "vertical" }} />
            </div>

            {/* ── Start timeframe ── */}
            <div style={{ marginBottom: 16 }}>
              <label style={labelStyle}>When are you looking to start?</label>
              <select value={form.start} onChange={set("start")}
                style={{ ...fieldStyle, background: "#111B2E", color: form.start ? "#F1F5F9" : "#94A3B8" }}>
                <option value="" disabled>Select a timeframe...</option>
                <option value="As soon as possible">As soon as possible</option>
                <option value="Within 2 weeks">Within 2 weeks</option>
                <option value="Within a month">Within a month</option>
                <option value="Flexible">I'm flexible</option>
              </select>
            </div>

            {/* ── Questions ── */}
            <div style={{ marginBottom: 28 }}>
              <label style={labelStyle}>Any questions before you enroll?</label>
              <textarea rows={2} value={form.question} onChange={set("question")}
                placeholder="Anything you'd like to know first..."
                style={{ ...fieldStyle, resize: "vertical" }} />
            </div>

            {/* ── Error message ── */}
            {error && (
              <div style={{ background: "rgba(248,113,113,0.1)", border: "1px solid rgba(248,113,113,0.3)", borderRadius: 10, padding: "10px 14px", marginBottom: 16, color: "#F87171", fontSize: 13 }}>
                {error}
              </div>
            )}

            {/* ── Submit ── */}
            <Btn
              onClick={handleSubmit}
              style={{
                width: "100%", justifyContent: "center",
                opacity: valid && !sending ? 1 : 0.5,
                cursor: valid && !sending ? "pointer" : "not-allowed",
              }}
            >
              {sending ? "Sending..." : isMentorship ? "Submit Application" : "Request Enrollment"}
              {!sending && <Icons.Arrow />}
            </Btn>
            <p style={{ color: "#475569", fontSize: 12, textAlign: "center", marginTop: 12, marginBottom: 0 }}>
              No payment required yet — I'll confirm your spot first.
            </p>
          </>
        )}
      </div>
    </div>
  );
};
