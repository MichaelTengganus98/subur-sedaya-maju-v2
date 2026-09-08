(function () {
	/* Mobile navigation */
	var navToggle = document.querySelector(".nav-toggle");
	var siteNav = document.querySelector(".site-nav");
	var navOverlay = document.getElementById("nav-overlay");

	function closeNav() {
		if (!navToggle || !siteNav) return;
		siteNav.classList.remove("is-open");
		navToggle.classList.remove("is-active");
		navToggle.setAttribute("aria-expanded", "false");
		if (navOverlay) navOverlay.classList.remove("is-active");
	}

	if (navToggle && siteNav) {
		navToggle.addEventListener("click", function () {
			var isOpen = siteNav.classList.toggle("is-open");
			navToggle.classList.toggle("is-active", isOpen);
			navToggle.setAttribute("aria-expanded", String(isOpen));
			if (navOverlay) navOverlay.classList.toggle("is-active", isOpen);
		});

		siteNav.querySelectorAll("a").forEach(function (link) {
			link.addEventListener("click", closeNav);
		});

		if (navOverlay) {
			navOverlay.addEventListener("click", closeNav);
		}
	}

	/* Sticky header shadow on scroll */
	var header = document.getElementById("site-header");
	if (header) {
		var onScroll = function () {
			header.classList.toggle("is-scrolled", window.scrollY > 8);
		};
		window.addEventListener("scroll", onScroll, { passive: true });
		onScroll();
	}

	/* Scroll-reveal animations */
	var revealEls = document.querySelectorAll(".reveal");
	if ("IntersectionObserver" in window && revealEls.length) {
		var observer = new IntersectionObserver(
			function (entries) {
				entries.forEach(function (entry) {
					if (entry.isIntersecting) {
						entry.target.classList.add("is-visible");
						observer.unobserve(entry.target);
					}
				});
			},
			{ threshold: 0.15, rootMargin: "0px 0px -40px 0px" }
		);
		revealEls.forEach(function (el) {
			observer.observe(el);
		});
	} else {
		revealEls.forEach(function (el) {
			el.classList.add("is-visible");
		});
	}

	/* Animated stat counters */
	var statNumbers = document.querySelectorAll(".stat-number");
	if ("IntersectionObserver" in window && statNumbers.length) {
		var countObserver = new IntersectionObserver(
			function (entries) {
				entries.forEach(function (entry) {
					if (!entry.isIntersecting) return;
					var el = entry.target;
					var target = parseInt(el.getAttribute("data-count"), 10) || 0;
					var duration = 1200;
					var start = null;

					function step(timestamp) {
						if (start === null) start = timestamp;
						var progress = Math.min((timestamp - start) / duration, 1);
						el.textContent = Math.floor(progress * target);
						if (progress < 1) {
							window.requestAnimationFrame(step);
						} else {
							el.textContent = target;
						}
					}

					window.requestAnimationFrame(step);
					countObserver.unobserve(el);
				});
			},
			{ threshold: 0.4 }
		);
		statNumbers.forEach(function (el) {
			countObserver.observe(el);
		});
	} else {
		statNumbers.forEach(function (el) {
			el.textContent = el.getAttribute("data-count");
		});
	}

	/* Footer year */
	var yearEl = document.getElementById("year");
	if (yearEl) {
		yearEl.textContent = new Date().getFullYear();
	}

	/* Contact form: submits natively as a POST to the Django `contact` app.
	   Progressive enhancement only — guard against double submits. */
	var form = document.getElementById("contact-form");
	if (form) {
		form.addEventListener("submit", function () {
			var btn = form.querySelector('button[type="submit"]');
			if (btn) {
				btn.disabled = true;
				btn.textContent = "Mengirim…";
			}
		});
	}
})();
