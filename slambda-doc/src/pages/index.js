import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import { Button, Typography } from '@mui/material';
import LibraryBooksIcon from '@mui/icons-material/LibraryBooks';
import styles from './index.module.css';

export default function Home() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="Description will go into a meta tag in <head />">
      <Box
        component={'main'}
        sx={{
          // background: "url('/img/bg.svg')",
          backgroundRepeat: "no-repeat",
          backgroundSize: 'contain',
          height: {
            // xs: '100%',
            // md: '90vh',
          },
          display: 'flex',
          flexDirection: 'column',
          alignItems: "center",
          pt: {
            xs: 6,
            md: 50
          },
          px: {
            xs: 6,
            md: 30
          },
          minWidth: '100%'
        }}>
        <Typography
          sx={{
            width: '100%'
          }}
          variant="h1"
          component="h2"
          fontWeight={'bold'}
        >
          {siteConfig.title}
        </Typography>
        <Typography
          sx={{
            width: '100%'
          }}
          variant="h4" component="h4"
        >
          {siteConfig.tagline}
        </Typography>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'row',
            alignItems: "center",
            justifyContent: 'flex-start',
            width: '100%',
            mt: 2,
          }}
        >
          <Button
            component={Link}
            href="/docs/intro"
            size='xl' variant='outlined'
            // color="#fff"
            startIcon={<LibraryBooksIcon />}
          >
            Getting Started
          </Button>
        </Box>

      </Box>
    </Layout>
  );
}
