    # Alias methods for compatibility
    async def get_adsets(self, *args, **kwargs):
        """Alias for get_ad_sets for compatibility."""
        return await self.get_ad_sets(*args, **kwargs)
    
    async def get_advanced_insights(self, account_id: str, start_date: str, end_date: str,
                                   level: str = "campaign", breakdowns: List[str] = None,
                                   metrics: List[str] = None, time_increment: str = "1") -> Dict[str, Any]:
        """
        Get advanced insights with breakdowns for in-depth analysis.
        
        Args:
            account_id: The ad account ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            level: Level of insights (campaign, adset, ad)
            breakdowns: List of breakdown dimensions
            metrics: List of metrics to retrieve
            time_increment: Time increment (1, 7, monthly, all_days)
            
        Returns:
            Advanced insights data with breakdowns
        """
        try:
            # Default advanced metrics for comprehensive analysis
            if not metrics:
                metrics = [
                    # Basic metrics
                    'spend', 'impressions', 'clicks', 'reach', 'frequency',
                    # Engagement metrics
                    'post_engagement', 'page_engagement', 'link_clicks',
                    # Video metrics
                    'video_play_actions', 'video_p25_watched_actions', 
                    'video_p50_watched_actions', 'video_p75_watched_actions',
                    'video_p100_watched_actions',
                    # Conversion metrics
                    'conversions', 'conversion_values', 'cost_per_conversion',
                    # Quality metrics
                    'quality_ranking', 'engagement_rate_ranking',
                    # Advanced metrics
                    'ctr', 'cpm', 'cpp', 'cpc'
                ]
            
            # Default breakdowns for comprehensive analysis
            if not breakdowns:
                breakdowns = [
                    'age', 'gender', 'country', 'region',
                    'device_platform', 'publisher_platform', 'platform_position'
                ]
            
            params = {
                'time_range': {
                    'since': start_date,
                    'until': end_date
                },
                'fields': metrics,
                'breakdowns': breakdowns,
                'time_increment': time_increment,
                'level': level
            }
            
            account = AdAccount(account_id)
            insights = account.get_insights(params=params)
            
            insights_data = [dict(insight) for insight in insights]
            
            return {
                'data': insights_data,
                'summary': self._calculate_advanced_summary(insights_data),
                'breakdowns_used': breakdowns,
                'metrics_used': metrics,
                'date_range': f"{start_date} to {end_date}",
                'level': level
            }
            
        except FacebookRequestError as e:
            self.logger.error(f"Error getting advanced insights: {e}")
            raise MetaAdsClientError(f"Failed to get advanced insights: {e}")
    
    async def get_creative_performance(self, account_id: str, date_range_days: int = 30) -> Dict[str, Any]:
        """
        Analyze creative performance and identify fatigue patterns.
        
        Args:
            account_id: The ad account ID
            date_range_days: Number of days to analyze
            
        Returns:
            Creative performance analysis
        """
        try:
            from datetime import datetime, timedelta
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=date_range_days)
            
            # Get ads with creative data
            ads = await self.get_ads(account_id)
            
            creative_performance = []
            
            for ad in ads[:10]:  # Limit to prevent API overuse
                try:
                    # Get insights for each ad
                    ad_insights = await self.get_insights(
                        account_id, 
                        start_date.strftime('%Y-%m-%d'),
                        end_date.strftime('%Y-%m-%d'),
                        ad_ids=ad['id']
                    )
                    
                    # Get creative details
                    creative_data = await self.get_ad_creatives(ad['id'])
                    
                    creative_performance.append({
                        'ad_id': ad['id'],
                        'ad_name': ad['name'],
                        'creative_id': creative_data.get('id'),
                        'creative_name': creative_data.get('name'),
                        'performance': ad_insights.get('data', []),
                        'created_time': ad.get('created_time'),
                        'updated_time': ad.get('updated_time')
                    })
                    
                except Exception as e:
                    self.logger.warning(f"Could not get creative data for ad {ad['id']}: {e}")
                    continue
            
            return {
                'creative_analysis': creative_performance,
                'summary': self._analyze_creative_fatigue(creative_performance),
                'date_range': f"Last {date_range_days} days",
                'total_creatives_analyzed': len(creative_performance)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing creative performance: {e}")
            raise MetaAdsClientError(f"Failed to analyze creative performance: {e}")
    
    async def get_demographic_insights(self, account_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get detailed demographic breakdown insights.
        
        Args:
            account_id: The ad account ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Demographic insights analysis
        """
        try:
            # Get insights with demographic breakdowns
            demographic_data = await self.get_advanced_insights(
                account_id, start_date, end_date,
                breakdowns=['age', 'gender', 'country'],
                metrics=['spend', 'impressions', 'clicks', 'conversions', 'ctr', 'cpm']
            )
            
            # Process demographic data for better analysis
            processed_data = self._process_demographic_data(demographic_data['data'])
            
            return {
                'demographic_breakdown': processed_data,
                'insights': demographic_data,
                'recommendations': self._generate_demographic_recommendations(processed_data)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting demographic insights: {e}")
            raise MetaAdsClientError(f"Failed to get demographic insights: {e}")
    
    async def get_device_performance(self, account_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Analyze performance across different devices and platforms.
        
        Args:
            account_id: The ad account ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Device and platform performance analysis
        """
        try:
            device_data = await self.get_advanced_insights(
                account_id, start_date, end_date,
                breakdowns=['device_platform', 'publisher_platform', 'platform_position'],
                metrics=['spend', 'impressions', 'clicks', 'conversions', 'ctr', 'cpm', 'cpc']
            )
            
            return {
                'device_analysis': self._analyze_device_performance(device_data['data']),
                'raw_data': device_data,
                'optimization_tips': self._generate_device_optimization_tips(device_data['data'])
            }
            
        except Exception as e:
            self.logger.error(f"Error getting device performance: {e}")
            raise MetaAdsClientError(f"Failed to get device performance: {e}")
    
    async def get_time_based_insights(self, account_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get time-based performance insights (hourly, daily patterns).
        
        Args:
            account_id: The ad account ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Time-based performance analysis
        """
        try:
            # Get hourly insights
            hourly_data = await self.get_advanced_insights(
                account_id, start_date, end_date,
                breakdowns=['hourly_stats_aggregated_by_advertiser_time_zone'],
                metrics=['spend', 'impressions', 'clicks', 'conversions'],
                time_increment='1'
            )
            
            return {
                'hourly_performance': self._analyze_hourly_performance(hourly_data['data']),
                'peak_hours': self._identify_peak_hours(hourly_data['data']),
                'recommendations': self._generate_timing_recommendations(hourly_data['data']),
                'raw_data': hourly_data
            }
            
        except Exception as e:
            self.logger.error(f"Error getting time-based insights: {e}")
            raise MetaAdsClientError(f"Failed to get time-based insights: {e}")

    def _calculate_advanced_summary(self, insights_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate advanced summary statistics from insights data."""
        if not insights_data:
            return {}
            
        try:
            import pandas as pd
            df = pd.DataFrame(insights_data)
            
            summary = {}
            
            # Advanced numeric fields
            numeric_fields = [
                'spend', 'impressions', 'clicks', 'reach', 'frequency',
                'post_engagement', 'page_engagement', 'link_clicks',
                'video_play_actions', 'conversions', 'conversion_values'
            ]
            
            for field in numeric_fields:
                if field in df.columns:
                    try:
                        df[field] = pd.to_numeric(df[field], errors='coerce')
                        summary[f'total_{field}'] = df[field].sum()
                        summary[f'avg_{field}'] = df[field].mean()
                        summary[f'max_{field}'] = df[field].max()
                        summary[f'min_{field}'] = df[field].min()
                    except:
                        pass
            
            # Advanced calculated metrics
            if 'total_clicks' in summary and 'total_impressions' in summary and summary['total_impressions'] > 0:
                summary['overall_ctr'] = (summary['total_clicks'] / summary['total_impressions']) * 100
                
            if 'total_spend' in summary and 'total_clicks' in summary and summary['total_clicks'] > 0:
                summary['overall_cpc'] = summary['total_spend'] / summary['total_clicks']
                
            if 'total_spend' in summary and 'total_conversions' in summary and summary['total_conversions'] > 0:
                summary['overall_cost_per_conversion'] = summary['total_spend'] / summary['total_conversions']
                
            if 'total_conversion_values' in summary and 'total_spend' in summary and summary['total_spend'] > 0:
                summary['overall_roas'] = summary['total_conversion_values'] / summary['total_spend']
            
            return summary
            
        except Exception as e:
            self.logger.warning(f"Error calculating advanced summary: {e}")
            return {}
    
    def _analyze_creative_fatigue(self, creative_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze creative performance for fatigue patterns."""
        try:
            fatigue_analysis = {
                'high_fatigue_creatives': [],
                'optimal_creatives': [],
                'recommendations': []
            }
            
            for creative in creative_data:
                performance = creative.get('performance', [])
                if not performance:
                    continue
                    
                # Simple fatigue analysis based on CTR decline
                try:
                    ctrs = [float(p.get('ctr', 0)) for p in performance if p.get('ctr')]
                    if len(ctrs) >= 3:  # Need at least 3 data points
                        recent_ctr = sum(ctrs[-3:]) / 3  # Last 3 periods
                        early_ctr = sum(ctrs[:3]) / 3    # First 3 periods
                        
                        if early_ctr > 0 and recent_ctr / early_ctr < 0.7:  # 30% decline
                            fatigue_analysis['high_fatigue_creatives'].append({
                                'creative_id': creative['creative_id'],
                                'creative_name': creative['creative_name'],
                                'ctr_decline': ((early_ctr - recent_ctr) / early_ctr) * 100
                            })
                        elif recent_ctr > early_ctr:
                            fatigue_analysis['optimal_creatives'].append({
                                'creative_id': creative['creative_id'],
                                'creative_name': creative['creative_name'],
                                'ctr_improvement': ((recent_ctr - early_ctr) / early_ctr) * 100
                            })
                except:
                    continue
            
            # Generate recommendations
            if fatigue_analysis['high_fatigue_creatives']:
                fatigue_analysis['recommendations'].append(
                    f"Consider refreshing {len(fatigue_analysis['high_fatigue_creatives'])} creatives showing fatigue"
                )
            
            if fatigue_analysis['optimal_creatives']:
                fatigue_analysis['recommendations'].append(
                    f"Scale up {len(fatigue_analysis['optimal_creatives'])} high-performing creatives"
                )
            
            return fatigue_analysis
            
        except Exception as e:
            self.logger.warning(f"Error analyzing creative fatigue: {e}")
            return {}
    
    def _process_demographic_data(self, demographic_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process demographic data for better insights."""
        try:
            import pandas as pd
            
            if not demographic_data:
                return {}
                
            df = pd.DataFrame(demographic_data)
            
            processed = {
                'age_performance': {},
                'gender_performance': {},
                'country_performance': {},
                'top_segments': []
            }
            
            # Age analysis
            if 'age' in df.columns:
                age_stats = df.groupby('age').agg({
                    'spend': 'sum',
                    'impressions': 'sum', 
                    'clicks': 'sum',
                    'conversions': 'sum'
                }).to_dict('index')
                processed['age_performance'] = age_stats
            
            # Gender analysis  
            if 'gender' in df.columns:
                gender_stats = df.groupby('gender').agg({
                    'spend': 'sum',
                    'impressions': 'sum',
                    'clicks': 'sum', 
                    'conversions': 'sum'
                }).to_dict('index')
                processed['gender_performance'] = gender_stats
            
            # Country analysis
            if 'country' in df.columns:
                country_stats = df.groupby('country').agg({
                    'spend': 'sum',
                    'impressions': 'sum',
                    'clicks': 'sum',
                    'conversions': 'sum'
                }).to_dict('index')
                processed['country_performance'] = country_stats
            
            return processed
            
        except Exception as e:
            self.logger.warning(f"Error processing demographic data: {e}")
            return {}
    
    def _generate_demographic_recommendations(self, demographic_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on demographic performance."""
        recommendations = []
        
        try:
            # Age recommendations
            age_perf = demographic_data.get('age_performance', {})
            if age_perf:
                best_age = max(age_perf.keys(), key=lambda x: age_perf[x].get('conversions', 0))
                recommendations.append(f"Best performing age group: {best_age}")
            
            # Gender recommendations  
            gender_perf = demographic_data.get('gender_performance', {})
            if gender_perf:
                best_gender = max(gender_perf.keys(), key=lambda x: gender_perf[x].get('conversions', 0))
                recommendations.append(f"Best performing gender: {best_gender}")
            
            # Country recommendations
            country_perf = demographic_data.get('country_performance', {})
            if country_perf:
                best_country = max(country_perf.keys(), key=lambda x: country_perf[x].get('conversions', 0))
                recommendations.append(f"Best performing country: {best_country}")
                
        except Exception as e:
            self.logger.warning(f"Error generating demographic recommendations: {e}")
        
        return recommendations 