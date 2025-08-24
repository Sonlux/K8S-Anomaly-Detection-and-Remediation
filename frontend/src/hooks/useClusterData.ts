
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { supabase } from '@/integrations/supabase/client';

interface ClusterDataItem {
  id: string;
  cluster_name: string;
  data_type: string;
  data: any;
  content_text?: string;
  created_at: string;
  updated_at: string;
}

export const useClusterData = () => {
  const queryClient = useQueryClient();

  const { data: clusterData, isLoading } = useQuery({
    queryKey: ['cluster-data'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('cluster_data')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) throw error;
      return data as ClusterDataItem[];
    },
  });

  const addClusterData = useMutation({
    mutationFn: async ({ dataType, data, contentText }: { 
      dataType: string; 
      data: any; 
      contentText?: string; 
    }) => {
      const { data: result, error } = await supabase
        .from('cluster_data')
        .insert({
          data_type: dataType,
          data: data,
          content_text: contentText || JSON.stringify(data)
        })
        .select()
        .single();

      if (error) throw error;
      return result;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cluster-data'] });
    },
  });

  return {
    clusterData,
    isLoading,
    addClusterData: addClusterData.mutate,
    isAdding: addClusterData.isPending,
  };
};
