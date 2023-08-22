import React from "react";
import {useNavigate, Link as RouterLink, useParams, Outlet} from "react-router-dom";
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import {Alert, Box, Link} from "@mui/material";
import {useAppContext, useAppContextAction} from "../features";
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';

export function MainAppLayout(props: {}) {
    const appCtx = useAppContext();
    const actions = useAppContextAction();
    const navigate = useNavigate();
    const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
    const open = Boolean(anchorEl);

    React.useEffect(() => {
        actions.updateStatus();
    }, [])

    const handleMenuOpen = (event: any) => {
        setAnchorEl(event.currentTarget);
    };

    const handleMenuClose = () => {
        setAnchorEl(null);
    };
    const handleMenuCloseAndNavigate = (url: string) => {
        setAnchorEl(null);
        navigate(url);
    };

    return <Box>
        <AppBar position="static" color={'secondary'}>
            <Toolbar
                sx={{display: 'flex', justifyContent: 'space-between'}}>
                <Box
                    sx={{display: 'flex', alignItems: 'center'}}>
                    <Link component={RouterLink} to={'/'}>
                        <img src={'/icon.png'} alt="Logo" style={{marginRight: '10px', height: '40px'}}/>
                    </Link>
                    <Link
                        color={'info'}
                        sx={{}}
                        underline={'none'}
                        component={RouterLink} to={'/'} variant="h5">Playground</Link>
                </Box>
                <IconButton color="inherit" aria-label="menu" onClick={handleMenuOpen}>
                    <MenuIcon/>
                </IconButton>
                <Menu
                    anchorEl={anchorEl}
                    open={open}
                    onClose={handleMenuClose}
                >
                    <MenuItem onClick={() => handleMenuCloseAndNavigate('/')}>View Functions</MenuItem>
                    <MenuItem onClick={() => handleMenuCloseAndNavigate('/logs')}>View Logs</MenuItem>
                </Menu>

            </Toolbar>
        </AppBar>
        {
            !appCtx.isReady && <Alert severity="warning">Connecting to playground server...</Alert>
        }

        {
            !appCtx.status.has_key && <Alert severity="warning">No OpenAI API Key detected, function may not be able to run.</Alert>
        }
        <Box sx={{
            p: 4,
            display: 'flex',
            flexDirection: 'column',
        }}>
            <Outlet/>
        </Box>
    </Box>
}