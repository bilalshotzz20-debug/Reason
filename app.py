
/* ==========================================
   REASON — ADVANCED ANIMATION SYSTEM
========================================== */

/* PAGE ENTRANCE */
@keyframes pageReveal {
    from {
        opacity: 0;
        transform: translateY(18px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.main .block-container {
    animation: pageReveal 0.8s ease-out;
}

/* SIDEBAR ENTRANCE */
@keyframes sidebarReveal {
    from {
        opacity: 0;
        transform: translateX(-25px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

[data-testid="stSidebar"] {
    animation: sidebarReveal 0.7s ease-out;
}

/* LOGO FLOAT */
@keyframes logoFloat {
    0%, 100% {
        transform: translateY(0);
    }
    50% {
        transform: translateY(-5px);
    }
}

.brand-icon {
    animation: logoFloat 3s ease-in-out infinite;
}

/* HEADER ANIMATION */
.topbar {
    animation: pageReveal 0.9s ease-out;
    transition: all 0.3s ease;
}

.topbar:hover {
    box-shadow: 0 10px 30px rgba(40,120,240,0.10);
    transform: translateY(-2px);
}

/* CARD ENTRANCE */
@keyframes cardReveal {
    from {
        opacity: 0;
        transform: translateY(20px) scale(0.98);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

[data-testid="stVerticalBlockBorderWrapper"] {
    animation: cardReveal 0.8s ease-out both;
    transition:
        transform 0.3s ease,
        box-shadow 0.3s ease,
        border-color 0.3s ease;
}

[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 14px 35px rgba(40,120,240,0.08);
    border-color: #BCD6FA !important;
}

/* CHAT MESSAGE ANIMATION */
@keyframes messageReveal {
    from {
        opacity: 0;
        transform: translateY(12px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

[data-testid="stChatMessage"] {
    animation: messageReveal 0.45s ease-out both;
}

/* BUTTON ANIMATION */
@keyframes buttonGlow {
    0%, 100% {
        box-shadow: 0 5px 13px rgba(40,120,240,0.14);
    }
    50% {
        box-shadow: 0 7px 23px rgba(40,120,240,0.30);
    }
}

.stButton > button,
.stDownloadButton > button {
    transition: all 0.25s ease !important;
    position: relative;
    overflow: hidden;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    transform: translateY(-3px) scale(1.01);
    animation: buttonGlow 1.5s infinite;
}

.stButton > button:active,
.stDownloadButton > button:active {
    transform: scale(0.97);
}

/* BUTTON SHIMMER */
.stButton > button::before,
.stDownloadButton > button::before {
    content: "";
    position: absolute;
    top: 0;
    left: -120%;
    width: 70%;
    height: 100%;
    background: linear-gradient(
        110deg,
        transparent,
        rgba(255,255,255,0.28),
        transparent
    );
    transition: left 0.6s ease;
    pointer-events: none;
}

.stButton > button:hover::before,
.stDownloadButton > button:hover::before {
    left: 130%;
}

/* REPORT BADGE PULSE */
@keyframes badgePulse {
    0%, 100% {
        box-shadow: 0 0 0 0 rgba(19,139,101,0.10);
    }
    50% {
        box-shadow: 0 0 0 6px rgba(19,139,101,0.06);
    }
}

.doctor-chip {
    animation: badgePulse 2.5s ease-in-out infinite;
}

/* REPORT CONTENT */
.report-title {
    animation: pageReveal 0.7s ease-out;
}

/* EMPTY REPORT ICON */
@keyframes documentFloat {
    0%, 100% {
        transform: translateY(0) rotate(0deg);
    }
    50% {
        transform: translateY(-8px) rotate(3deg);
    }
}

.empty-icon {
    animation: documentFloat 3s ease-in-out infinite;
}

/* FILE UPLOADER */
[data-testid="stFileUploader"] {
    transition: all 0.3s ease;
    background-size: 200% 200%;
}

[data-testid="stFileUploader"]:hover {
    border-color: #2878F0;
    background: #EEF6FF;
    transform: translateY(-2px);
}

/* TABS */
.stTabs [data-baseweb="tab"] {
    transition: all 0.25s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #2878F0 !important;
    transform: translateY(-2px);
}

/* SIDEBAR HOVER */
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    transition: all 0.25s ease;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p:hover {
    color: #2878F0 !important;
    transform: translateX(5px);
}

/* SOFT BACKGROUND MOTION */
@keyframes backgroundFlow {
    0%, 100% {
        background-position: 0% 50%;
    }
    50% {
        background-position: 100% 50%;
    }
}

.stApp {
    background: linear-gradient(
        120deg,
        #F7FAFF,
        #EFF6FF,
        #F8FAFF,
        #F1F7FF
    ) !important;
    background-size: 300% 300% !important;
    animation: backgroundFlow 18s ease infinite;
}

/* ACCESSIBILITY */
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
