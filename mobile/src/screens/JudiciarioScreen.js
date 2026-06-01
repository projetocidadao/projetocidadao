/**
 * JudiciárioScreen - Dados do Judiciário
 */
import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, FlatList } from 'react-native';
import { getTribunais, getEstatisticas } from '../services/api';

const JudiciarioScreen = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('tribunais');

  const loadTribunais = async () => {
    setLoading(true);
    try {
      const response = await getTribunais();
      setData(response.data?.dados || []);
    } catch (error) {
      console.error(error);
    }
    setLoading(false);
  };

  const loadEstatisticas = async () => {
    setLoading(true);
    try {
      const response = await getEstatisticas();
      setData(response.data?.dados || []);
    } catch (error) {
      console.error(error);
    }
    setLoading(false);
  };

  const renderItem = ({ item }) => (
    <View style={styles.item}>
      <Text style={styles.itemTitle}>{item.descricao || item.nome}</Text>
      <Text style={styles.itemSubtitle}>{item.codigo || item.sigla}</Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Judiciário</Text>
      
      <View style={styles.tabs}>
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'tribunais' && styles.activeTab]}
          onPress={() => { setActiveTab('tribunais'); loadTribunais(); }}
        >
          <Text style={styles.tabText}>Tribunais</Text>
        </TouchableOpacity>
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'estatisticas' && styles.activeTab]}
          onPress={() => { setActiveTab('estatisticas'); loadEstatisticas(); }}
        >
          <Text style={styles.tabText}>Estatísticas</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        data={data}
        renderItem={renderItem}
        keyExtractor={(item, index) => index.toString()}
        style={styles.list}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#8e44ad',
    marginBottom: 16,
  },
  tabs: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  tab: {
    flex: 1,
    padding: 10,
    backgroundColor: '#ddd',
    alignItems: 'center',
  },
  activeTab: {
    backgroundColor: '#8e44ad',
  },
  tabText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  list: {
    flex: 1,
  },
  item: {
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  itemTitle: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  itemSubtitle: {
    fontSize: 12,
    color: '#7f8c8d',
  },
});

export default JudiciarioScreen;