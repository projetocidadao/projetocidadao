/**
 * LegislativoScreen - Dados do Legislativo
 */
import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, FlatList } from 'react-native';
import { getDeputados, getProposicoes, getSenadores } from '../services/api';

const LegislativoScreen = () => {
  const [search, setSearch] = useState('');
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('deputados');

  const searchDeputados = async () => {
    setLoading(true);
    try {
      const response = await getDeputados(search);
      setData(response.data?.dados || []);
    } catch (error) {
      console.error(error);
    }
    setLoading(false);
  };

  const searchProposicoes = async () => {
    setLoading(true);
    try {
      const response = await getProposicoes(2024);
      setData(response.data?.dados || []);
    } catch (error) {
      console.error(error);
    }
    setLoading(false);
  };

  const searchSenadores = async () => {
    setLoading(true);
    try {
      const response = await getSenadores(search);
      setData(response.data?.dados || []);
    } catch (error) {
      console.error(error);
    }
    setLoading(false);
  };

  const renderItem = ({ item }) => (
    <View style={styles.item}>
      <Text style={styles.itemTitle}>
        {item.nome || item.siglaTipo + ' ' + item.numero}
      </Text>
      <Text style={styles.itemSubtitle}>
        {item.siglaUf || item.ementa?.substring(0, 80)}
      </Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Legislativo</Text>
      
      <View style={styles.tabs}>
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'deputados' && styles.activeTab]}
          onPress={() => setActiveTab('deputados')}
        >
          <Text style={styles.tabText}>Deputados</Text>
        </TouchableOpacity>
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'proposicoes' && styles.activeTab]}
          onPress={() => setActiveTab('proposicoes')}
        >
          <Text style={styles.tabText}>Proposições</Text>
        </TouchableOpacity>
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'senadores' && styles.activeTab]}
          onPress={() => setActiveTab('senadores')}
        >
          <Text style={styles.tabText}>Senadores</Text>
        </TouchableOpacity>
      </View>

      <TextInput
        style={styles.input}
        placeholder="Buscar..."
        value={search}
        onChangeText={setSearch}
      />

      <TouchableOpacity style={styles.button} onPress={
        activeTab === 'deputados' ? searchDeputados :
        activeTab === 'proposicoes' ? searchProposicoes : searchSenadores
      }>
        <Text style={styles.buttonText}>Buscar</Text>
      </TouchableOpacity>

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
    color: '#2980b9',
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
    backgroundColor: '#2980b9',
  },
  tabText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  input: {
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 8,
    marginBottom: 12,
  },
  button: {
    backgroundColor: '#2980b9',
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 16,
  },
  buttonText: {
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

export default LegislativoScreen;