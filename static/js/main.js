(function () {
  // Scroll-reveal: each .reveal section fades/slides in once as it enters
  // the viewport. Falls back to showing everything immediately if
  // IntersectionObserver isn't available.
  const revealEls = document.querySelectorAll(".reveal");
  if (revealEls.length) {
    if ("IntersectionObserver" in window) {
      const observer = new IntersectionObserver(
        (entries, obs) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              entry.target.classList.add("is-visible");
              obs.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.12, rootMargin: "0px 0px -8% 0px" }
      );
      revealEls.forEach((el) => observer.observe(el));
    } else {
      revealEls.forEach((el) => el.classList.add("is-visible"));
    }
  }

  // Sticky mobile "Book a Call" bar, shown after scrolling past ~70% of viewport height.
  const stickyCta = document.getElementById("sticky-cta");
  if (stickyCta) {
    const updateSticky = () => {
      const show = window.scrollY > window.innerHeight * 0.7;
      stickyCta.hidden = !show;
    };
    window.addEventListener("scroll", updateSticky, { passive: true });
    updateSticky();
  }

  // Lead capture form: POST to /api/leads, swap to a thank-you card on success.
  const form = document.getElementById("lead-form");
  if (form) {
    const successCard = document.getElementById("lead-success");
    const formError = document.getElementById("lead-form-error");
    const nameError = document.getElementById("lead-name-error");
    const phoneError = document.getElementById("lead-phone-error");

    const clearErrors = () => {
      formError.textContent = "";
      nameError.textContent = "";
      phoneError.textContent = "";
    };

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      clearErrors();

      const submitBtn = form.querySelector("button[type=submit]");
      submitBtn.disabled = true;

      const payload = {
        name: form.elements["name"].value,
        phone: form.elements["phone"].value,
      };

      try {
        const res = await fetch("/api/leads", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const data = await res.json();

        if (res.ok && data.success) {
          form.hidden = true;
          successCard.hidden = false;
        } else if (data.errors) {
          if (data.errors.name) nameError.textContent = data.errors.name;
          if (data.errors.phone) phoneError.textContent = data.errors.phone;
        } else {
          formError.textContent = "Something went wrong. Please try again.";
        }
      } catch (err) {
        formError.textContent = "Something went wrong. Please check your connection and try again.";
      } finally {
        submitBtn.disabled = false;
      }
    });
  }
})();
