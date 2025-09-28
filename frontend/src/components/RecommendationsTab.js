import React, { useState } from 'react';
import styled from 'styled-components';
import { Search, Package, Star, TrendingUp, Filter, Loader } from 'lucide-react';
import { useMutation, useQuery } from 'react-query';
import toast from 'react-hot-toast';
import { getRecommendations, getCategories } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const RecommendationsContainer = styled.div`
  max-width: 1000px;
  margin: 0 auto;
`;

const SearchForm = styled.form`
  background: ${props => props.theme.colors.surface};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.xl};
  margin-bottom: ${props => props.theme.spacing.xl};
  box-shadow: ${props => props.theme.shadows.md};
`;

const FormTitle = styled.h2`
  font-size: 1.5rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.lg};
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
`;

const SearchTypeSelector = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.sm};
  margin-bottom: ${props => props.theme.spacing.lg};
  background: ${props => props.theme.colors.background};
  padding: ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius.md};

  @media (max-width: 640px) {
    flex-direction: column;
  }
`;

const SearchTypeButton = styled.button`
  flex: 1;
  padding: ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.md};
  border: 2px solid ${props => props.active ? props.theme.colors.primary : 'transparent'};
  background: ${props => props.active ? props.theme.colors.primary : 'transparent'};
  color: ${props => props.active ? 'white' : props.theme.colors.text};
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${props => props.theme.spacing.sm};

  &:hover {
    background: ${props => props.active ? props.theme.colors.primaryDark : props.theme.colors.background};
  }
`;

const InputGroup = styled.div`
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const Label = styled.label`
  display: block;
  font-weight: 500;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const Input = styled.input`
  width: 100%;
  padding: ${props => props.theme.spacing.md};
  border: 2px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.2s ease;

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
  }

  &::placeholder {
    color: ${props => props.theme.colors.textSecondary};
  }
`;

const Select = styled.select`
  width: 100%;
  padding: ${props => props.theme.spacing.md};
  border: 2px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 1rem;
  font-family: inherit;
  background: white;
  cursor: pointer;
  transition: border-color 0.2s ease;

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
  }
`;

const ControlsRow = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.md};
  align-items: end;

  @media (max-width: 640px) {
    flex-direction: column;
    align-items: stretch;
  }
`;

const SliderContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.xs};
`;

const SliderLabel = styled.label`
  font-size: 0.875rem;
  font-weight: 500;
  color: ${props => props.theme.colors.text};
`;

const Slider = styled.input`
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: ${props => props.theme.colors.border};
  outline: none;
  -webkit-appearance: none;

  &::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: ${props => props.theme.colors.primary};
    cursor: pointer;
  }

  &::-moz-range-thumb {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: ${props => props.theme.colors.primary};
    cursor: pointer;
    border: none;
  }
`;

const SliderValue = styled.span`
  font-size: 0.875rem;
  color: ${props => props.theme.colors.textSecondary};
  text-align: center;
`;

const SubmitButton = styled.button`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.xl};
  background: ${props => props.theme.colors.primary};
  color: white;
  border: none;
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 140px;
  justify-content: center;

  &:hover:not(:disabled) {
    background: ${props => props.theme.colors.primaryDark};
    transform: translateY(-1px);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const ResultsSection = styled.div`
  background: ${props => props.theme.colors.surface};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.xl};
  margin-bottom: ${props => props.theme.spacing.xl};
  box-shadow: ${props => props.theme.shadows.md};
`;

const ResultsHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: ${props => props.theme.spacing.lg};

  @media (max-width: 640px) {
    flex-direction: column;
    align-items: stretch;
    gap: ${props => props.theme.spacing.md};
  }
`;

const ResultsTitle = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin: 0;
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
`;

const ResultsCount = styled.span`
  background: ${props => props.theme.colors.primary};
  color: white;
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius.sm};
  font-size: 0.875rem;
  font-weight: 600;
`;

const ProductCard = styled.div`
  background: ${props => props.theme.colors.background};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.xl};
  margin-bottom: ${props => props.theme.spacing.lg};
  transition: all 0.2s ease;

  &:hover {
    border-color: ${props => props.theme.colors.primary};
    box-shadow: ${props => props.theme.shadows.md};
    transform: translateY(-2px);
  }
`;

const ProductHeader = styled.div`
  display: flex;
  align-items: start;
  justify-content: space-between;
  margin-bottom: ${props => props.theme.spacing.md};

  @media (max-width: 640px) {
    flex-direction: column;
    gap: ${props => props.theme.spacing.sm};
  }
`;

const ProductTitle = styled.h4`
  font-size: 1.125rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin: 0;
  flex: 1;
  line-height: 1.4;
`;

const ProductMeta = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
  flex-wrap: wrap;
`;

const RatingContainer = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
  color: ${props => props.theme.colors.textSecondary};
  font-size: 0.875rem;
`;

const CategoryTag = styled.span`
  background: ${props => props.theme.colors.primary};
  color: white;
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius.sm};
  font-size: 0.75rem;
  font-weight: 500;
`;

const SimilarityScore = styled.div`
  background: ${props => props.theme.colors.success};
  color: white;
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius.sm};
  font-size: 0.75rem;
  font-weight: 600;
`;

const ProductDescription = styled.div`
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const Rationale = styled.p`
  color: ${props => props.theme.colors.textSecondary};
  font-size: 0.875rem;
  line-height: 1.6;
  margin: 0;
  padding: ${props => props.theme.spacing.md};
  background: ${props => props.theme.colors.background};
  border-radius: ${props => props.theme.borderRadius.md};
  border-left: 4px solid ${props => props.theme.colors.primary};
`;

const ReviewSnippets = styled.div`
  margin-top: ${props => props.theme.spacing.lg};
`;

const SnippetsTitle = styled.h5`
  font-size: 1rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.md};
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
`;

const SnippetCard = styled.div`
  background: ${props => props.theme.colors.background};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  padding: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.sm};
  font-size: 0.875rem;
  line-height: 1.6;
  color: ${props => props.theme.colors.textSecondary};
`;

const ChartsSection = styled.div`
  margin-top: ${props => props.theme.spacing.xl};
`;

const ChartsTitle = styled.h4`
  font-size: 1.125rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.lg};
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
`;

const ChartsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: ${props => props.theme.spacing.lg};
`;

const ChartContainer = styled.div`
  background: ${props => props.theme.colors.background};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.lg};
`;

const ChartTitle = styled.h5`
  font-size: 1rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.md};
  text-align: center;
`;

const RecommendationsTab = () => {
  const [searchType, setSearchType] = useState('text_query');
  const [query, setQuery] = useState('');
  const [productId, setProductId] = useState('');
  const [category, setCategory] = useState('');
  const [topK, setTopK] = useState(10);
  const [minSimilarity, setMinSimilarity] = useState(0.3);

  // Fetch categories
  const { data: categories = [] } = useQuery('categories', getCategories, {
    enabled: searchType === 'category_top',
  });

  const getRecommendationsMutation = useMutation(getRecommendations, {
    onSuccess: (data) => {
      toast.success(`Found ${data.total_found} recommendations!`);
    },
    onError: (error) => {
      toast.error('Failed to get recommendations. Please try again.');
      console.error('Error:', error);
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();

    let requestData = { top_k: topK, min_similarity: minSimilarity };

    if (searchType === 'text_query' && !query.trim()) {
      toast.error('Please enter a search query');
      return;
    }
    if (searchType === 'product_similar' && !productId.trim()) {
      toast.error('Please enter a product ID');
      return;
    }
    if (searchType === 'category_top' && !category) {
      toast.error('Please select a category');
      return;
    }

    switch (searchType) {
      case 'text_query':
        requestData.query = query;
        break;
      case 'product_similar':
        requestData.product_id = productId;
        break;
      case 'category_top':
        requestData.category = category;
        break;
    }

    getRecommendationsMutation.mutate(requestData);
  };

  const result = getRecommendationsMutation.data;
  const recommendations = result?.recommendations || [];

  // Prepare chart data
  const ratingData = recommendations.map(rec => ({
    name: rec.product_title.substring(0, 20) + '...',
    rating: rec.average_rating,
    reviews: rec.num_reviews
  }));

  const similarityData = recommendations.map(rec => ({
    name: rec.product_title.substring(0, 15) + '...',
    similarity: rec.similarity_score
  }));

  const COLORS = ['#FF9900', '#FFB84D', '#FFCC80', '#FFE0B3', '#FFF4E6'];

  return (
    <RecommendationsContainer>
      <SearchForm onSubmit={handleSubmit}>
        <FormTitle>
          <Search size={24} />
          Product Recommendations
        </FormTitle>

        <SearchTypeSelector>
          <SearchTypeButton
            type="button"
            active={searchType === 'text_query'}
            onClick={() => setSearchType('text_query')}
          >
            <Search size={16} />
            Text Query
          </SearchTypeButton>
          <SearchTypeButton
            type="button"
            active={searchType === 'product_similar'}
            onClick={() => setSearchType('product_similar')}
          >
            <Package size={16} />
            Similar Products
          </SearchTypeButton>
          <SearchTypeButton
            type="button"
            active={searchType === 'category_top'}
            onClick={() => setSearchType('category_top')}
          >
            <TrendingUp size={16} />
            Category Top
          </SearchTypeButton>
        </SearchTypeSelector>

        {searchType === 'text_query' && (
          <InputGroup>
            <Label htmlFor="query">Describe what you're looking for</Label>
            <Input
              id="query"
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., wireless headphones with good battery life"
              disabled={getRecommendationsMutation.isLoading}
            />
          </InputGroup>
        )}

        {searchType === 'product_similar' && (
          <InputGroup>
            <Label htmlFor="productId">Product ID</Label>
            <Input
              id="productId"
              type="text"
              value={productId}
              onChange={(e) => setProductId(e.target.value)}
              placeholder="e.g., B08N5WRWNW"
              disabled={getRecommendationsMutation.isLoading}
            />
          </InputGroup>
        )}

        {searchType === 'category_top' && (
          <InputGroup>
            <Label htmlFor="category">Select Category</Label>
            <Select
              id="category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              disabled={getRecommendationsMutation.isLoading}
            >
              <option value="">Choose a category...</option>
              {categories.map((cat, index) => (
                <option key={index} value={cat}>{cat}</option>
              ))}
            </Select>
          </InputGroup>
        )}

        <ControlsRow>
          <SliderContainer>
            <SliderLabel>Max Results: {topK}</SliderLabel>
            <Slider
              type="range"
              min="1"
              max="50"
              value={topK}
              onChange={(e) => setTopK(parseInt(e.target.value))}
              disabled={getRecommendationsMutation.isLoading}
            />
            <SliderValue>1-50 results</SliderValue>
          </SliderContainer>

          <SliderContainer>
            <SliderLabel>Min Similarity: {minSimilarity.toFixed(1)}</SliderLabel>
            <Slider
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={minSimilarity}
              onChange={(e) => setMinSimilarity(parseFloat(e.target.value))}
              disabled={getRecommendationsMutation.isLoading}
            />
            <SliderValue>0.0-1.0</SliderValue>
          </SliderContainer>

          <SubmitButton type="submit" disabled={getRecommendationsMutation.isLoading}>
            {getRecommendationsMutation.isLoading ? (
              <Loader size={20} className="animate-spin" />
            ) : (
              <Search size={20} />
            )}
            {getRecommendationsMutation.isLoading ? 'Searching...' : 'Get Recommendations'}
          </SubmitButton>
        </ControlsRow>
      </SearchForm>

      {result && (
        <ResultsSection>
          <ResultsHeader>
            <ResultsTitle>
              <Package size={20} />
              Recommendations
              <ResultsCount>{result.total_found}</ResultsCount>
            </ResultsTitle>
          </ResultsHeader>

          {recommendations.length === 0 ? (
            <p style={{ textAlign: 'center', color: '#64748B', padding: '2rem' }}>
              No recommendations found. Try adjusting your search criteria.
            </p>
          ) : (
            <>
              {recommendations.map((rec, index) => (
                <ProductCard key={index}>
                  <ProductHeader>
                    <ProductTitle>#{index + 1} {rec.product_title}</ProductTitle>
                    <ProductMeta>
                      <RatingContainer>
                        <Star size={16} />
                        {rec.average_rating}/5 ({rec.num_reviews} reviews)
                      </RatingContainer>
                      <CategoryTag>{rec.category}</CategoryTag>
                      <SimilarityScore>{rec.similarity_score.toFixed(3)}</SimilarityScore>
                    </ProductMeta>
                  </ProductHeader>

                  <ProductDescription>
                    <Rationale>{rec.rationale}</Rationale>
                  </ProductDescription>

                  {rec.review_snippets && rec.review_snippets.length > 0 && (
                    <ReviewSnippets>
                      <SnippetsTitle>
                        <Star size={16} />
                        Review Snippets ({rec.review_snippets.length})
                      </SnippetsTitle>
                      {rec.review_snippets.map((snippet, snippetIndex) => (
                        <SnippetCard key={snippetIndex}>
                          "{snippet}"
                        </SnippetCard>
                      ))}
                    </ReviewSnippets>
                  )}
                </ProductCard>
              ))}

              {recommendations.length > 1 && (
                <ChartsSection>
                  <ChartsTitle>
                    <TrendingUp size={20} />
                    Analysis Charts
                  </ChartsTitle>

                  <ChartsGrid>
                    <ChartContainer>
                      <ChartTitle>Rating Distribution</ChartTitle>
                      <ResponsiveContainer width="100%" height={200}>
                        <BarChart data={ratingData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="name" />
                          <YAxis />
                          <Tooltip />
                          <Bar dataKey="rating" fill="#FF9900" />
                        </BarChart>
                      </ResponsiveContainer>
                    </ChartContainer>

                    <ChartContainer>
                      <ChartTitle>Similarity Scores</ChartTitle>
                      <ResponsiveContainer width="100%" height={200}>
                        <PieChart>
                          <Pie
                            data={similarityData}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, similarity }) => `${name}: ${similarity.toFixed(2)}`}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="similarity"
                          >
                            {similarityData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip />
                        </PieChart>
                      </ResponsiveContainer>
                    </ChartContainer>
                  </ChartsGrid>
                </ChartsSection>
              )}
            </>
          )}
        </ResultsSection>
      )}
    </RecommendationsContainer>
  );
};

export default RecommendationsTab;
