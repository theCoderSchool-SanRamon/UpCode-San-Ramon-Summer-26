import { createApp } from 'vue'
import Map from 'ol/Map.js';
import OSM from 'ol/source/OSM.js';
import TileLayer from 'ol/layer/Tile.js';
import View from 'ol/View.js';

import App from './components/App.vue'
import './style.css'
import 'ol/ol.css';


createApp(App).mount('#app')
