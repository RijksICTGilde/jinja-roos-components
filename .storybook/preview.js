const preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    options: {
      storySort: {
        order: ["Introductie", "Aan de slag", "Brand", "Layout", "Componenten"],
      },
    },
  },
  decorators: [
    (story) => {
      const wrapper = document.createElement("div");
      wrapper.classList.add("rvo-theme");
      const rendered = story();
      if (typeof rendered === "string") {
        wrapper.innerHTML = rendered;
      } else {
        wrapper.appendChild(rendered);
      }
      return wrapper;
    },
  ],
};

export default preview;
