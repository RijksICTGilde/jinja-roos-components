const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const HtmlWebpackDeployPlugin = require("html-webpack-deploy-plugin");
const ReplaceInFileWebpackPlugin = require("replace-in-file-webpack-plugin");

module.exports = {
  mode: 'development',
  entry: './fe_src/ts/roos.ts',
  output: {
    filename: 'roos.js',
    path: path.resolve(__dirname, 'jinja_roos_components/static/dist'),
    publicPath: '/static/roos/dist/',
    library: 'roos',
    libraryTarget: 'umd',
    clean: true,
  },
  devtool: 'source-map',
  module: {
    rules: [
      {
        test: /\.ts$/i,
        use: 'ts-loader',
        exclude: /node_modules/
      },
      {
        test: /\.s[ac]ss$/i,
        use: [
          MiniCssExtractPlugin.loader,
          "css-loader",
          {
            loader: "sass-loader",
            options: {
              sourceMap: true,
              sassOptions: {
                outputStyle: "expanded",
              },
            },
          },
        ],
      },
    ]
  },
  resolve: {
    extensions: ['.ts', '.js']
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: 'jinja_roos_components/templates/layouts/base.html.j2.webpack',
      filename: path.resolve(__dirname, 'jinja_roos_components/templates/layouts/base.html.j2'),
      inject: false
    }),
    new HtmlWebpackPlugin({
      template: 'jinja_roos_components/templates/components/page.html.j2.webpack',
      filename: path.resolve(__dirname, 'jinja_roos_components/templates/components/page.html.j2'),
      inject: false
    }),
    new HtmlWebpackDeployPlugin({
      usePackagesPath: false,
      getPackagePath: (packageName, packageVersion, packagePath) => path.join(packageName, packagePath),
      packages: {
        '@nl-rvo/assets': {
          copy: [
            { from: 'fonts', to: 'fonts/'},
            { from: 'icons', to: 'icons/'},
            { from: 'images', to: 'images/'}
          ],
          links: [
            'fonts/index.css',
            'icons/index.css',
            'images/index.css',
          ]
        },
        '@nl-rvo/design-tokens': {
          copy: [
            { from: 'dist/index.css', to: 'index.css' },
            { from: 'dist/index.js', to: 'index.mjs' },
          ],
          links: [
            'index.css',
          ],
          scripts: [
            'index.mjs',
          ]
        },
        '@nl-rvo/component-library-css': {
          copy: [
            { from: 'dist/index.css', to: 'index.css' },
          ],
          links: [
            'index.css',
          ]
        },
        '@nl-rvo/css-button': {
          copy: [
            { from: 'dist/index.css', to: 'index.css' },
          ],
          links: [
            'index.css',
          ]
        },
      }
    }),
    new MiniCssExtractPlugin({
      filename: "roos.css",
      chunkFilename: "[id].css",
    }),
    new ReplaceInFileWebpackPlugin([{
      dir: 'jinja_roos_components/static/dist/@nl-rvo/assets/icons/',
      files: ['index.css'],
      rules: [{
        search: /url\("(?!\/)/ig,
        replace: 'url("/static/roos/dist/@nl-rvo/assets/icons/'
      }]
    }])
  ]
};