/** @type {import('@storybook/html-webpack5').StorybookConfig} */
const config = {
  stories: [
    "../storybook/stories/**/*.stories.js",
    "../storybook/docs/**/*.mdx",
    "../storybook/docs/**/*.stories.js",
  ],
  addons: ["@storybook/addon-essentials", "@storybook/addon-a11y"],
  framework: {
    name: "@storybook/html-webpack5",
    options: {},
  },
  staticDirs: [
    {
      from: "../src/jinja_roos_components/static/roos/dist",
      to: "/static/roos/dist",
    },
  ],
};

export default config;
