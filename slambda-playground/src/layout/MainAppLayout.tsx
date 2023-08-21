import React from "react";
import {useNavigate, Link as RouteLink, useParams, Outlet} from "react-router-dom";
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import {Box} from "@mui/material";
import {useAppContext, useAppContextAction} from "../features";
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';

export function MainAppLayout(props: {}) {
    const appCtx = useAppContext();
    const actions = useAppContextAction();
    const navigate = useNavigate();
    const [menuAnchor, setMenuAnchor] = React.useState<any>(null);
    React.useEffect(() => {
        actions.updateStatus();
    }, [])

    const handleMenuOpen = (event: any) => {
        setMenuAnchor(event.currentTarget);
    };

    const handleMenuClose = (url: string) => {
        setMenuAnchor(null);
        navigate(url);
    };

    return <Box>
        <AppBar position="static">
            <Toolbar sx={{display: 'flex', justifyContent: 'space-between'}}>
                <Box sx={{display: 'flex', alignItems: 'center'}}>
                    <img src={'/icon.png'} alt="Logo" style={{marginRight: '10px', height: '40px'}}/>
                    <Typography variant="h5">Playground</Typography>
                </Box>
                <IconButton color="inherit" aria-label="menu" onClick={handleMenuOpen}>
                    <MenuIcon/>
                </IconButton>
                <Menu
                    anchorEl={menuAnchor}
                    open={Boolean(menuAnchor)}
                    onClose={handleMenuClose}
                >
                    <MenuItem onClick={() => handleMenuClose('')}>Option 3</MenuItem>
                    <MenuItem onClick={() => handleMenuClose('/')}>View Functions</MenuItem>
                    <MenuItem onClick={() => handleMenuClose('/logs')}>View Logs</MenuItem>
                </Menu>

            </Toolbar>
        </AppBar>
        <Box>
            <Outlet/>
        </Box>
    </Box>
}