// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require('prism-react-renderer/themes/github');
const darkCodeTheme = require('prism-react-renderer/themes/dracula');

/** @type {import('@docusaurus/types').Config} */
const config = {
    title: 'sλ',
    tagline: "instruction is function",
    favicon: 'img/favicon.ico',

    // Set the production url of your site here
    url: 'https://slambda.dataset.sh',
    // Set the /<baseUrl>/ pathname under which your site is served
    // For GitHub pages deployment, it is often '/<projectName>/'
    baseUrl: '/',

    scripts: [{src: 'https://plausible.io/js/script.js', defer: true, 'data-domain': 'slambda.dataset.sh'}],

    // GitHub pages deployment config.
    // If you aren't using GitHub pages, you don't need these.
    organizationName: 'dataset.sh', // Usually your GitHub org/user name.
    projectName: 'slambda', // Usually your repo name.

    onBrokenLinks: 'throw',
    onBrokenMarkdownLinks: 'warn',

    // Even if you don't use internalization, you can use this field to set useful
    // metadata like html lang. For example, if your site is Chinese, you may want
    // to replace "en" with "zh-Hans".
    i18n: {
        defaultLocale: 'en',
        locales: ['en', 'zh'],
    },

    presets: [
        [
            'classic',
            /** @type {import('@docusaurus/preset-classic').Options} */
            ({
                docs: {
                    sidebarPath: require.resolve('./sidebars.js'),
                    // Please change this to your repo.
                    // Remove this to remove the "edit this page" links.
                    // editUrl:
                    // 'https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/',
                },
                blog: {
                    showReadingTime: true,
                    // Please change this to your repo.
                    // Remove this to remove the "edit this page" links.
                    // editUrl:
                    // 'https://github.com/dataset-sh/slambda/tree/main/slambda-doc/create-docusaurus/templates/shared/',
                },
                theme: {
                    customCss: require.resolve('./src/css/custom.css'),
                },
            }),
        ],
    ],

    themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
        ({
            // Replace with your project's social card
            image: 'img/slambda-social-large.png',
            colorMode: {
                defaultMode: 'light',
                disableSwitch: true,
                respectPrefersColorScheme: false,
            },
            metadata: [
                {
                    name: 'keywords',
                    content: 'nlp, entailment, nli, chatgpt, openai, api, model, text function, sentiment'
                },
                {name: 'twitter:card', content: 'summary_large_image'},
            ],
            navbar: {
                title: 'sLambda',
                logo: {
                    alt: 'sLambda Logo',
                    src: 'img/logo.svg',
                },
                items: [
                    {
                        type: 'docSidebar',
                        sidebarId: 'tutorialSidebar',
                        position: 'left',
                        label: 'Docs',
                    },
                    { to: '/blog', label: 'Blog', position: 'left' },
                    {
                        type: 'localeDropdown',
                        position: 'right',
                      },
                    {
                        href: 'https://github.com/dataset-sh/slambda',
                        label: 'GitHub',
                        position: 'right',
                    },
                ],
            },
            footer: {
                style: 'dark',
                links: [
                    {
                        title: 'Docs',
                        items: [
                            {
                                label: 'Getting Started',
                                to: '/docs/intro',
                            },
                        ],
                    },
                    {
                        title: 'Community',
                        items: [
                            {
                                label: 'Discussion',
                                href: 'https://github.com/dataset-sh/slambda/discussions',
                            },
                            // {
                            //     label: 'Discord',
                            //     href: 'https://discordapp.com/invite/docusaurus',
                            // },
                            // {
                            //     label: 'Twitter',
                            //     href: 'https://twitter.com/docusaurus',
                            // },
                        ],
                    },
                    {
                        title: 'More',
                        items: [
                            // {
                            //   label: 'Blog',
                            //   to: '/blog',
                            // },
                            {
                                label: 'GitHub',
                                href: 'https://github.com/dataset-sh/slambda',
                            },
                        ],
                    },
                ],
                copyright: `Copyright © ${new Date().getFullYear()} ORANGE ON THE COB TECHNOLOGY CORP. Built with Docusaurus.`,
            },
            prism: {
                theme: lightCodeTheme,
                darkTheme: darkCodeTheme,
            },
        }),

    themes: [
        // ... Your other themes.
        [
            require.resolve("@easyops-cn/docusaurus-search-local"),
            /** @type {import("@easyops-cn/docusaurus-search-local").PluginOptions} */
            ({
                // ... Your options.
                // `hashed` is recommended as long-term-cache of index file is possible.
                hashed: true,
                // For Docs using Chinese, The `language` is recommended to set to:
                // ```
                // language: ["en", "zh"],
                // ```
            }),
        ],
    ],

};

module.exports = config;
